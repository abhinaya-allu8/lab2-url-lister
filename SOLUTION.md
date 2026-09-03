
# Lab 2 – Convert WordCount to URLCount

## Overview

For this lab, I modified the Hadoop WordCount example into a URLCount application using Python and Hadoop Streaming.

The program reads two Wikipedia HTML pages, extracts URL references contained inside href attributes, counts how many times each URL occurs across the input files, and outputs only URLs whose final count is greater than 5.

I first developed and tested the program using the CSEL Hadoop 3.3.6 environment. After verifying that it worked correctly, I deployed the same program to Google Cloud Dataproc and tested it using two cluster configurations:

- 1 master node + 2 worker nodes
- 1 master node + 4 worker nodes

## Implementation Choice

I implemented URLCount using Hadoop Streaming with Python.

The main files are:

- URLMapper.py
- URLReducer.py
- Makefile

## Mapper Logic

The mapper reads the Wikipedia HTML input line-by-line from standard input.

I used Python's re module to extract values contained inside HTML href attributes.

The regular expression used is:

    href_pattern = re.compile(r'href=["\'](.*?)["\']', re.IGNORECASE)

For every URL found, the mapper outputs the URL as the key and 1 as the value.

A single HTML input line may contain multiple links, so the mapper can emit multiple URL/count pairs for one input line.

The mapper also ignores links equal to # because they do not represent useful URL references for this lab.

## Shuffle and Sort

After the map phase, Hadoop performs shuffle and sort.

This groups mapper output by URL before sending it to the reducer. Identical URLs become adjacent, allowing the reducer to calculate the total count for each URL.

## Reducer Logic

The reducer receives mapper output sorted by URL.

It keeps track of the current URL and adds together all counts associated with that URL.

Only URLs whose final count is greater than 5 are written to the output.

The count filtering is done in the reducer because only the reducer sees the complete set of values for a URL after Hadoop's shuffle and sort phase.

## Why Filtering Must Happen in the Reducer

The count > 5 condition cannot safely be applied in the mapper because each mapper only processes part of the input.

For example, one mapper may see a URL 3 times and another mapper may see the same URL 3 times. Each mapper individually sees a count of only 3, but the final global count is 6.

Therefore, filtering in the mapper could incorrectly remove a URL that should appear in the final output.

## Combiner Discussion

The original Java WordCount implementation uses a combiner to reduce intermediate data.

For normal WordCount, a combiner is safe because addition is associative and partial sums can be combined later.

However, applying the count > 5 filtering rule inside a combiner would be incorrect.

A combiner only sees a partial set of values for a URL. For example, one mapper may produce a partial count of 3 and another mapper may also produce a partial count of 3. If the combiner discarded both because they were not greater than 5, the reducer would never see the correct global count of 6.

Therefore, a combiner may safely perform partial summation, but filtering based on count > 5 must happen only after final aggregation in the reducer.

## CSEL Testing

I first tested the mapper using:

    echo '<a href="/wiki/MapReduce">MapReduce</a>' | python3 URLMapper.py

I also tested multiple URLs on the same line.

Then I tested the mapper and reducer together using:

    cat input/file01 input/file02 | python3 URLMapper.py | sort | python3 URLReducer.py

The sort command approximates Hadoop's shuffle-and-sort behavior.

After this worked, I ran the implementation using Hadoop Streaming in the CSEL Hadoop 3.3.6 environment.

Both Wikipedia files were loaded into HDFS:

    input/file01
    input/file02

## Google Cloud Dataproc

After verifying the program on CSEL, I ran the same URLCount implementation on Google Cloud Dataproc.

I used two cluster configurations:

- 1 master node + 2 worker nodes
- 1 master node + 4 worker nodes

On Dataproc, the Hadoop Streaming JAR was located at:

    /usr/lib/hadoop/hadoop-streaming-3.3.6.jar

This path differed from the CSEL Hadoop Streaming path, so the Makefile path had to be adjusted before running the job.

## Execution Time Comparison

I measured execution time using:

    time make stream

Results:

| Cluster Configuration | Real Time | User Time | System Time |
| --- | ---: | ---: | ---: |
| 1 master + 2 workers | 1m 30.880s | 15.713s | 1.022s |
| 1 master + 4 workers | 1m 47.249s | 14.458s | 0.918s |

The 2-worker cluster completed the job faster than the 4-worker cluster.

The 4-worker cluster took approximately 16.369 seconds longer.

This was somewhat surprising because adding workers might be expected to improve performance. However, the dataset is small, and Hadoop introduces overhead from job initialization, task scheduling, network communication, shuffle and sort, process startup, HDFS access, and coordination between worker nodes.

For this workload, the additional coordination overhead of the 4-worker cluster outweighed the benefit of extra parallelism.

This demonstrates that adding more machines does not automatically make a distributed application faster. The workload must be large enough for the benefits of parallelism to outweigh the coordination overhead.

## Software Used

- Python 3
- Python re module
- Apache Hadoop 3.3.6
- Hadoop Streaming
- HDFS
- GNU Make
- Git
- GitHub
- CSEL Coding environment
- Google Cloud Platform
- Google Cloud Dataproc

## Resources Used

- Course Lab 2 README
- Apache Hadoop MapReduce documentation
- Hadoop Streaming documentation
- Python regular expression documentation
- GeeksforGeeks URL extraction examples
- Google Cloud Dataproc documentation

## Collaboration

I completed the implementation independently.
EOF
