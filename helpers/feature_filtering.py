--- current/tools_patterns.py
+++ proposed/tools_patterns.py
@@ -0,0 +1,217 @@
+import os
+import tempfile
+import numpy as np
+import pandas as pd
+from typing import Dict, Any, List, Optional, Literal
+
+from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
+from langchain_core.tools import tool
+
+# Import PAMI frequent pattern algorithms
+from PAMI.frequentPattern.basic import FPGrowth
+from PAMI.frequentPattern.topk import FAE
+from PAMI.frequentPattern.maximal import MaxFPGrowth
+
+
+def make_tools(session: Any) -> list:
+    """Factory function returning tools for frequent pattern mining."""
+
+    @tool
+    def mine_patterns_tool(
+        category_name: str,
+        filtering_method: Literal["variance", "tfidf", "term_frequency"],
+        algorithm: Literal["fpgrowth", "topk", "maxfpgrowth"] = "fpgrowth",
+        min_sup: Optional[int] = 1,
+        k: Optional[int] = 1
+    ) -> Dict[str, Any]:
+        """Mines frequent patterns for a specific document category using PAMI algorithms.
+
+        Filters category text using variance, TF-IDF, or term frequency, converts to a transactional
+        database, and mines patterns using FPGrowth, Top-K (FAE), or MaxFPGrowth.
+
+        Args:
+            category_name: Name of category to filter and mine (e.g. 'catA' or 'catB').
+            filtering_method: Vocabulary filtering method ('variance', 'tfidf', or 'term_frequency').
+            algorithm: PAMI mining algorithm ('fpgrowth', 'topk', or 'maxfpgrowth').
+            min_sup: Minimum support integer threshold for 'fpgrowth' and 'maxfpgrowth'.
+            k: Number of top patterns to return for 'topk' algorithm.
+
+        Returns:
+            Dict containing result_id, category_name, filtering_method, algorithm,
+            kept_terms, patterns list, and pattern_count.
+        """
+        if session.dataframe is None or session.dataframe.empty:
+            return {"error": "No dataset loaded in session state."}
+
+        cat_col = "category_name" if "category_name" in session.dataframe.columns else ("label" if "label" in session.dataframe.columns else None)
+        if cat_col is None:
+            return {"error": "Category column not found in session.dataframe."}
+
+        # Step 1: Filter dataframe to category_name
+        cat_df = session.dataframe[session.dataframe[cat_col] == category_name]
+        if cat_df.empty:
+            return {"error": f"No documents found for category '{category_name}'."}
+
+        texts = cat_df["text"].fillna("").astype(str).tolist()
+
+        # Step 1b: Fit category-local CountVectorizer(stop_words="english")
+        vectorizer = CountVectorizer(stop_words="english")
+        try:
+            X_cat = vectorizer.fit_transform(texts)
+            feature_names = np.array(vectorizer.get_feature_names_out())
+        except ValueError:
+            # Handles empty vocabulary
+            feature_names = np.array([])
+            X_cat = None
+
+        if len(feature_names) == 0:
+            result_id = session.next_result_id("mine_patterns")
+            summary = {
+                "result_id": result_id,
+                "category_name": category_name,
+                "filtering_method": filtering_method,
+                "algorithm": algorithm,
+                "kept_terms": [],
+                "patterns": [],
+                "pattern_count": 0,
+                "note": "no terms survived stopword removal"
+            }
+            return summary
+
+        X_dense = X_cat.toarray()
+
+        # Step 2: Apply vocabulary filtering
+        if filtering_method == "variance":
+            scores = np.var(X_dense, axis=0)
+            low_p, high_p = np.percentile(scores, 5), np.percentile(scores, 95)
+            mask = (scores > low_p) & (scores < high_p)
+        elif filtering_method == "term_frequency":
+            scores = np.sum(X_dense, axis=0)
+            low_p, high_p = np.percentile(scores, 5), np.percentile(scores, 95)
+            mask = (scores > low_p) & (scores < high_p)
+        elif filtering_method == "tfidf":
+            transformer = TfidfTransformer()
+            tfidf_matrix = transformer.fit_transform(X_cat)
+            scores = np.mean(tfidf_matrix.toarray(), axis=0)
+            p20 = np.percentile(scores, 20)
+            mask = scores >= p20
+        else:
+            return {"error": f"Unsupported filtering method: {filtering_method}"}
+
+        kept_terms = feature_names[mask].tolist()
+
+        # Step 3: Handle zero terms kept
+        if len(kept_terms) == 0:
+            result_id = session.next_result_id("mine_patterns")
+            summary = {
+                "result_id": result_id,
+                "category_name": category_name,
+                "filtering_method": filtering_method,
+                "algorithm": algorithm,
+                "kept_terms": [],
+                "patterns": [],
+                "pattern_count": 0,
+                "note": "no terms survived filtering"
+            }
+            args = {
+                "category_name": category_name,
+                "filtering_method": filtering_method,
+                "algorithm": algorithm,
+                "min_sup": min_sup,
+                "k": k
+            }
+            session.store_result("mine_patterns_tool", args, summary)
+            return summary
+
+        # Step 4: Convert to Transactional Database for PAMI
+        kept_indices = np.where(mask)[0]
+        X_kept = X_dense[:, kept_indices]
+
+        # Build list of transactions (words present in document with count >= 1)
+        transactions = []
+        for row in X_kept:
+            items = [kept_terms[i] for i in range(len(kept_terms)) if row[i] >= 1]
+            if items:
+                transactions.append(items)
+
+        if not transactions:
+            result_id = session.next_result_id("mine_patterns")
+            summary = {
+                "result_id": result_id,
+                "category_name": category_name,
+                "filtering_method": filtering_method,
+                "algorithm": algorithm,
+                "kept_terms": kept_terms,
+                "patterns": [],
+                "pattern_count": 0,
+                "note": "no non-empty transactions for survived terms"
+            }
+            return summary
+
+        # Create temporary file for PAMI transactional database
+        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp_file:
+            tmp_db_path = tmp_file.name
+            for transaction in transactions:
+                tmp_file.write("\t".join(transaction) + "\n")
+
+        patterns_list = []
+
+        try:
+            effective_min_sup = min_sup if min_sup is not None else 1
+            effective_k = k if k is not None else 1
+
+            if algorithm == "fpgrowth":
+                miner = FPGrowth.FPGrowth(iFile=tmp_db_path, minSup=effective_min_sup, sep="\t")
+                miner.startMine()
+                patterns_df = miner.getPatternsAsDataFrame()
+            elif algorithm == "topk":
+                miner = FAE.FAE(iFile=tmp_db_path, k=effective_k, sep="\t")
+                miner.startMine()
+                patterns_df = miner.getPatternsAsDataFrame()
+            elif algorithm == "maxfpgrowth":
+                miner = MaxFPGrowth.MaxFPGrowth(iFile=tmp_db_path, minSup=effective_min_sup, sep="\t")
+                miner.startMine()
+                patterns_df = miner.getPatternsAsDataFrame()
+            else:
+                return {"error": f"Unsupported algorithm: {algorithm}"}
+
+            if patterns_df is not None and not patterns_df.empty:
+                for _, row in patterns_df.iterrows():
+                    pat_str = str(row["Patterns"])
+                    pat_items = pat_str.split("\t") if "\t" in pat_str else pat_str.split()
+                    sup_val = int(row["Support"])
+                    patterns_list.append({
+                        "pattern": pat_items,
+                        "support": sup_val
+                    })
+        finally:
+            if os.path.exists(tmp_db_path):
+                os.remove(tmp_db_path)
+
+        # Step 5: Store results and artifacts
+        artifact_key = f"patterns_{category_name}_{filtering_method}_{algorithm}"
+        session.artifacts[artifact_key] = patterns_list
+
+        result_id = session.next_result_id("mine_patterns")
+        summary = {
+            "result_id": result_id,
+            "category_name": category_name,
+            "filtering_method": filtering_method,
+            "algorithm": algorithm,
+            "kept_terms": kept_terms,
+            "patterns": patterns_list,
+            "pattern_count": len(patterns_list)
+        }
+
+        args = {
+            "category_name": category_name,
+            "filtering_method": filtering_method,
+            "algorithm": algorithm,
+            "min_sup": min_sup,
+            "k": k
+        }
+        session.store_result("mine_patterns_tool", args, summary)
+
+        return summary
+
+    return [mine_patterns_tool]