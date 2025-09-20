---
title: "Choosing between Dictionary Lookup and Join in PySpark"
date: "2025-09-18"
draft: false
---
Consider that I have data on budget allocation to eight departments in 1000 hospitals across 30 days. I'm working in PySpark and want to add a new column to the data: if the department is one of `["emergency", "cardiology", "surgery"]`, the column value should be `"critical_care"` and `"other"` otherwise. To create this column, my first instinct was to create a new dataframe containing this mapping between departments and the class (`critical_care` or `other`) and join it with the existing dataframe. But I learnt today that for small lookups, it is faster to perform a dictionary lookup in PySpark instead.

There is a 40-50% improvement in execution time for creating the new column. This is because, behind the scenes, a dictionary lookup is converted to a `CASE WHEN` expression or equivalent by the Spark query engine. Because this is a per-row expression, it avoids shuffles and inter-partition communication. On the other hand, a join operation involves the following steps:
1. The mapping table is broadcasted to all executor nodes which involves serialisation and deserialisation of the dataframe.
2. The mapping table needs to be managed in the executor memory.
3. A hash table needs to be constructed for the lookup and merge operations.

Past roughly a few dozen conditions, the generated expression can get large, so a broadcast join is often faster. This is a good rule of thumb to keep in mind.

For further understanding of the data, the operations, and the difference in execution times, please read and execute the associated [Jupyter notebook](../../notebooks/dict_vs_joins.ipynb).