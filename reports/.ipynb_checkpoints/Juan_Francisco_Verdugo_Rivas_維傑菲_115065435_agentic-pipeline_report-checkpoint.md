# Your report

*(Replace this with your own report: 3-5 short paragraphs. For each major step you actually ran, loading the data, filtering, pattern mining, dimension reduction, whatever applies, say what you did, reference the specific `result_id` and/or saved plot, and explain what it shows. Delete this instruction text before submitting.)*

Report on Agentic Pipeline

This report covers the process of appplying the 18 tools created in the AgenticDev Workbook to the 20 Newsgroups data set.

The first tool used was load_dataset_tool to load the 20 Newgroup dataset including the four categories of alt.atheism, soc.religion.christian, comp.graphics, and sci.med. The result is that it creates the object in the session called load_dataset_1. After that, inspect_data_tool was used to get a few rows of the dataset. The tool returns the first five rows of the dataset if the user does not specify a seed for a random selection. After that, two tools where executed (one at a time) check_missing_tool and check_duplicates tool. Neither missing values or duplicated values were found.

To further inspect the data, describe_data_tool was used, which returns descriptive statistics of the dataset in general and by category in the object describe_data_2. It found a total of 2,257 documents. The mean length of the characters in the documents was of 1,992.96 with a standard deviation of 3,547.66. The descriptive statistics showed a similar behaviour between categories. The one that highlights was the comp.graphics, which has a mean of 1,557.08 characters, but a maximum of 60,713 characters. It is the longest distance between the mean and the max value in a category. This can be visualized in the boxplot where comp.graphics has around three outliers with a length of more than 50,000 characters.

![Box plot of the length of documents by category](../plots/Juan_Francisco_Verdugo_Rivas_維傑菲_agentic-pipeline_plot_describe_data_2.png)

After inspecting the data, sample_data_tool was created using a frac value of 0.20 and a random_state of 42. It returned a dataframe of 451 row in sample_data_3. This tool at the start of the excercise only returned the table and some descriptive statistics of it but it did not save the data in a file for future use. For this reason, the sample_data_tool was modified so it saves a file if a path is given.

In the next step, the build_dtm_tool was used to create the document-term matrix. It resulted in a vocabulary size of 355,482 terms with a 99.6772% of sparsity (result_id: dtm_4). The build_dtm_tool runs by default stop_words = 'english'. With the document-term matrix built, the term_frequency_tool was used to retrieve data about the frequency of each word. Stored in term_freq_5, the top 5 most frequent terms where: edu (4,675), subject (2,464), lines (2,353), god (2,216), and organization (2,192).

For visualizing the frequency, the dtm_heatmap_tool was used. First, it retrieved a graph with a lot of 0s that did not communicate useful information. The problem was that it was build without the possibility to order first the the terms by frequency. After modifying the tool, it was instructed to build the heatmap but first to sort the terms in descending order by frequency.

![Heatmap graph without sorting terms](../plots/Juan_Francisco_Verdugo_Rivas_維傑菲_agentic-pipeline_plot_dtm_heatmap_6.png)
![Heatmap graph after sorting terms](../plots/Juan_Francisco_Verdugo_Rivas_維傑菲_agentic-pipeline_plot_dtm_heatmap_7.png)







