# Report on agentic pipeline

This report covers the process of appplying the 18 tools created in the AgenticDev Workbook to the 20 Newsgroups data set.

The first tool used was load_dataset_tool to load the 20 Newgroup dataset including the four categories of alt.atheism, soc.religion.christian, comp.graphics, and sci.med. The result is that it creates the object in the session called load_dataset_1 with a total of 2,257 documents. After that, inspect_data_tool was used to get a few rows of the dataset. The tool returns the first five rows of the dataset if the user does not specify a seed for a random selection. After that, two tools where executed (one at a time) check_missing_tool and check_duplicates_tool. Neither missing values or duplicated values were found (check_missing_3 and check_missing_4).

To further inspect the data, describe_data_tool was used, which returns descriptive statistics of the dataset in general and by category in the object describe_data_5. It found a total of 2,257 documents. The mean length of the characters in the documents was of 1,992.961 with a standard deviation of 3,547.656. The descriptive statistics showed a similar behaviour between categories. The one that highlights was the comp.graphics, which has a mean of 1,557.08 characters, but a maximum of 60,713 characters. It is the longest distance between the mean and the max value in a category. Also, comp.graphics is the category with the greatest standard deviation. This can be visualized in the boxplot where comp.graphics has around three outliers with a length of more than 50,000 characters.

![Box plot of the length of documents by category](../plots/Juan_Francisco_Verdugo_Rivas_維傑菲_agentic-pipeline_plot_describe_data_5.png)

After inspecting the data, sample_data_tool was created using a frac value of 0.20 and a random_state of 42. It returned a dataframe of 451 row in sample_data_3. This tool at the start of the excercise only returned the table and some descriptive statistics of it but it did not save the data in a file for future use. For this reason, the sample_data_tool was modified so it saves a file if a path is given.

In the next step, the build_dtm_tool was used to create the document-term matrix. It resulted in a vocabulary size of 35,482 terms with a 99.68% of sparsity (result_id: dtm_7). The build_dtm_tool runs by default stop_words = 'english'. With the document-term matrix built, the term_frequency_tool was used to retrieve data about the frequency of each word. Stored in term_freq_8, the top 5 most frequent terms where: edu (4,675), subject (2,464), lines (2,353), god (2,216), and organization (2,192).

For visualizing the frequency, the dtm_heatmap_tool was used. First, it retrieved a graph with a lot of 0s that did not communicate useful information. The problem was that it was build without the possibility to order first the the terms by frequency. After modifying the tool, it was instructed to build the heatmap but first to sort the terms in descending order by frequency.

![Heatmap graph without sorting terms](/plots/Juan_Francisco_Verdugo_Rivas_維傑菲_agentic-pipeline_plot_dtm_heatmap_9.png)
![Heatmap graph after sorting terms](../plots/Juan_Francisco_Verdugo_Rivas_維傑菲_agentic-pipeline_plot_dtm_heatmap_10.png)

After this process, the three tools for filtering were used. These are the reults from each tool:
- Variance_filter_tool:
    - **result_id:** variance_filter_15
    - **Threshold:** 0.05
    - **Terms before filtering:** 17,289
    - **Terms kept**: 35
    - **Terms removed** 17,254
- pearson_filter_tool:
    - **result_id:** pearson_filter_22
    - **Threshold:** 0.01
    - **Terms removed:** 0
- spearman_filter_tool:
    - **result_id:** spearman_filter_23
    - **Threshold:** 0.01
    - **Terms removed:** 0

To see the correlation, feature_correlation_matrix_tool was used. First the default value was used but the numeric values of the heatmap did not fit well. Therefore, the number of terms was reduced to 15.

![Feature correlation matrix](../plots/Juan_Francisco_Verdugo_Rivas_維傑菲_agentic-pipeline_plot_feat_corr_24.png)

The tool visualize_result_tool was used with the frequency data.

![Visualization of term frequency](../plots/Juan_Francisco_Verdugo_Rivas_維傑菲_agentic-pipeline_plot_turn92.png)


To mine the patterns the mine_patterns_tool was used with these parameters:
- **category_name:** soc.religion.christian. It was choosen due to personal interest with the topic.
- **filtering_method:** tfidf. It was choosen to keep the most informative terms.
- **algorithm:** topk with a k value of 20. It is considered a robust algorithm.
- **Results:** the 20 item has a support of 326, which is high (id:mine_patterns_27).

To visualize dimensionality reduction, reduce_dimensions_tool was used using umap method. Then it was done with 2 and 3 dimensions. This tool was created first to only make 2D graphs, it was necessary to return to the development phase so it could handle 3D graphs.

![Dimensionality reduction 2D](../plots/Juan_Francisco_Verdugo_Rivas_維傑菲_agentic-pipeline_plot_reduce_dim_28.png)
![Dimensionality reduction 3D](../plots/Juan_Francisco_Verdugo_Rivas_維傑菲_agentic-pipeline_plot_reduce_dim_29.png)

The command binarize_labels_tool was used and the result was stored in binarize_labels_30. Then it was used inspect_data_tool with a random seed of 42 to retrieve 5 random documents. Cosine_similarity_tool was used with two of the random documents obtained (index 440 and index 1360) which where from the soc.religion.christian category. The cosine similarity was 0.

