---
aliases:
- /2013/07/processing-planck-sources-with-hadoop
categories:
- hpc
- python
date: 2013-07-15 08:16
layout: post
slug: processing-planck-sources-with-hadoop
title: Processing sources in Planck maps with Hadoop and Python

---

<h2>
 Purpose
</h2>
<div>
 The purpose of this post is to investigate how to process in parallel sources extracted from full sky maps, in this case the maps release by Planck, using Hadoop instead of more traditional MPI-based HPC custom software.
</div>
<div>
 Hadoop is the MapReduce implementation most used in the enterprise world and it has been traditionally used to process huge amount of text data (~ TBs) , e.g. web pages or logs, over thousands commodity computers connected over ethernet.
</div>
<div>
 It allows to distribute the data across the nodes on a distributed file-system (HDFS) and then analyze them ("map" step) locally on each node, the output of the map step is traditionally a set of text (key, value) pairs, that are then sorted by the framework and passed to the "reduce" algorithm, which typically aggregates them and then save them to the distributed file-system.
</div>
<div>
 Hadoop gives robustness to this process by rerunning failed jobs, distribute the data with redundancy and re-distribute in case of failures, among many other features.
</div>
<div>
 Most scientist use HPC supercomputers for running large data processing software. Using HPC is necessary for algorithms that require frequent communication across the nodes, implemented via MPI calls over a dedicated high speed network (e.g. infiniband). However, often HPC resources are used for running a large number of jobs that are loosely coupled, i.e. each job runs mostly independently of the others, just a sort of aggregation is performed at the end. In this cases the use of a robust and flexible framework like Hadoop could be beneficial.
</div>
<div>
 <a name="more">
 </a>
</div>
<h2>
 Problem description
</h2>
<div>
 The Planck collaboration (btw I'm part of it...) released in May 2013 a set of full sky maps in Temperature at 9 different frequencies and catalogs of point and extended galactic and extragalactic sources:
</div>
<div>
 <a href="http://irsa.ipac.caltech.edu/Missions/planck.html">
  http://irsa.ipac.caltech.edu/Missions/planck.html
 </a>
</div>
<div>
 Each catalog contains about 1000 sources, and the collaboration released the location and flux of each source.
</div>
<div>
 The purpose of the analysis is to read each of the sky maps, slice out the section of the map around each source and perform some analysis on that patch of sky, as a simple example, to test the infrastructure, I am just going to compute the mean of the pixels located 10 arcminutes around the center of each source.
</div>
<div>
 In a production run, we might for example run aperture photometry on each source, or fitting for the source center to check for pointing accuracy.
</div>
<h2>
 Sources
</h2>
All files are available on github:
<br/>
<div>
 <a href="https://github.com/zonca/planck-sources-hadoop">
  https://github.com/zonca/planck-sources-hadoop
 </a>
</div>
<h2>
 Hadoop setup
</h2>
<div>
 I am running on the San Diego Supercomputing data intensive cluster Gordon:
</div>
<div>
 <a href="http://www.sdsc.edu/us/resources/gordon/">
  http://www.sdsc.edu/us/resources/gordon/
 </a>
</div>
<div>
 SDSC has a simplified Hadoop setup based on shell scripts,
 <a href="http://www.sdsc.edu/us/resources/gordon/gordon_hadoop.html">
  myHadoop
 </a>
 , which allows running Hadoop as a regular PBS job.
</div>
<div>
 The most interesting feature is that the Hadoop distributed file-system HDFS is setup on the low-latency local flash drives, one of the distinctive features of Gordon.
</div>
<h3>
 Using Python with Hadoop-streaming
</h3>
<div>
 Hadoop applications run natively in Java, however thanks to Hadoop-streaming, we can use stdin and stdout to communicate with a script implemented in any programming language.
</div>
<div>
 One of the most common choices for scientific applications is Python.
</div>
<h3>
 Application design
</h3>
<div>
 Best way to decrease the coupling between different parallel jobs for this application is, instead of analyzing one source at a time, analyze a patch of sky at a time, and loop through all the sources in that region.
</div>
<div>
 Therefore the largest amount data, the sky map, is only read once by a process, and all the sources are processed. I pre-process the sky map by splitting it in 10x10 degrees patches, saving a 2 columns array with pixel index and map temperature (
 <a href="https://github.com/zonca/planck-sources-hadoop/blob/master/preprocessing.py">
  preprocessing.py
 </a>
 ).
</div>
<div>
 Of course this will produce jobs whose length might be very different, due to the different effective sky area at poles and at equator, and by random number of source per patch, but that's something we do not worry about, that is exactly what Hadoop takes care of.
</div>
<h2>
 Implementation
</h2>
<h3>
 Input data
</h3>
<div>
 The pre-processed patches of sky are available in binary format on a lustre file-system shared by the processes.
</div>
<div>
 Therefore the text input files for the hadoop jobs are just the list of filenames of the sky patches, one per row.
</div>
<h3>
 Mapper
</h3>
<div>
 <a href="https://github.com/zonca/planck-sources-hadoop/blob/master/mapper.py">
  mapper.py
 </a>
</div>
<div>
 <br/>
</div>
<div>
 The mapper is fed by Hadoop via stdin with a number of lines extracted from the input files and returns a (key, value) text output for each source and for each statistics we compute on the source.
</div>
<div>
 In this simple scenario, the only returned key printed to stdout is "SOURCENAME_10arcminmean".
</div>
<div>
 For example, we can run a serial test by running:
</div>
<div>
 <br/>
</div>
<div>
 <div>
  <span style="font-family: Courier New, Courier, monospace;">
   echo plancktest/submaps/030_045_025 | ./mapper.py
  </span>
 </div>
</div>
<div>
 <span style="font-family: Courier New, Courier, monospace;">
  <br/>
 </span>
</div>
<div>
 <span style="font-family: inherit;">
  and the returned output is:
 </span>
</div>
<div>
 <span style="font-family: inherit;">
  <br/>
 </span>
</div>
<div>
 <div>
  <span style="font-family: Courier New, Courier, monospace;">
   PCCS1 030 G023.00+40.77_10arcminmean
   <span class="Apple-tab-span" style="white-space: pre;">
   </span>
   4.49202e-04
  </span>
 </div>
 <div>
  <span style="font-family: Courier New, Courier, monospace;">
   PCCS1 030 G023.13+42.14_10arcminmean
   <span class="Apple-tab-span" style="white-space: pre;">
   </span>
   3.37773e-04
  </span>
 </div>
 <div>
  <span style="font-family: Courier New, Courier, monospace;">
   PCCS1 030 G023.84+45.26_10arcminmean
   <span class="Apple-tab-span" style="white-space: pre;">
   </span>
   4.69427e-04
  </span>
 </div>
 <div>
  <span style="font-family: Courier New, Courier, monospace;">
   PCCS1 030 G024.32+48.81_10arcminmean
   <span class="Apple-tab-span" style="white-space: pre;">
   </span>
   3.79832e-04
  </span>
 </div>
 <div>
  <span style="font-family: Courier New, Courier, monospace;">
   PCCS1 030 G029.42+43.41_10arcminmean
   <span class="Apple-tab-span" style="white-space: pre;">
   </span>
   4.11600e-04
  </span>
 </div>
 <div style="font-family: inherit;">
  <br/>
 </div>
</div>
<h3>
 Reducer
</h3>
<div>
 There is no need for a reducer in this scenario, so Hadoop will just use the default IdentityReducer, which just aggregates all the mappers outputs to a single output file.
</div>
<h3>
 Hadoop call
</h3>
<div>
 <a href="https://github.com/zonca/planck-sources-hadoop/blob/master/run.pbs">
  run.pbs
 </a>
</div>
<div>
 <br/>
</div>
<div>
 The hadoop call is:
</div>
<div>
 <br/>
</div>
<div>
 <div>
  <span style="font-family: Courier New, Courier, monospace;">
   <code>
    $HADOOP_HOME/bin/hadoop --config $HADOOP_CONF_DIR jar $HADOOP_HOME/contrib/streaming/hadoop*streaming*.jar -file $FOLDER/mapper.py -mapper $FOLDER/mapper.py -input /user/$USER/Input/* -output /user/$USER/Output
   </code>
  </span>
 </div>
</div>
<div>
 <br/>
</div>
<div>
 So we are using the Hadoop-streaming interface and providing just the mapper, the input text files (list of sources) had been already copied to HDFS, the output needs then to be copied from HDFS to the local file-system, see run.pbs.
</div>
<h2>
 Hadoop run and results
</h2>
<div>
 For testing purposes we have just used 2 of the 9 maps (30 and 70 GHz), and processed all the total of ~2000 sources running Hadoop on 4 nodes.
</div>
<div>
 Processing takes about 5 minutes, Hadoop automatically chooses the number of mappers, and in this case only uses 2 mappers, as I think it reserves a couple of nodes to run the Scheduler and auxiliary processes.
</div>
<div>
 The outputs of the mappers are then joined, sorted and written on a single file, see the output file
</div>
<div>
 <a href="https://github.com/zonca/planck-sources-hadoop/blob/master/output/SAMPLE_RESULT_part-00000">
  output/SAMPLE_RESULT_part-00000
 </a>
 .
</div>
<div>
 See the full log
 <a href="https://github.com/zonca/planck-sources-hadoop/blob/master/sample_logs.txt">
  sample_logs.txt
 </a>
 extracted running:
</div>
<div>
 <span style="font-family: Courier New, Courier, monospace;">
  /opt/hadoop/bin/hadoop job -history output
 </span>
</div>
<h3>
 <span style="font-family: inherit;">
  Comparison of the results with the catalog
 </span>
</h3>
<div>
 <span style="font-family: inherit;">
  Just for a rough consistency check, I compared the normalized temperatures computed with Hadoop using just the mean of the pixels in a radius of 10 arcmin to the fluxes computed by the Planck collaboration. I find a general agreement with the expected noise excess.
 </span>
</div>
<div>
 <br/>
 <div class="separator" style="clear: both; text-align: left;">
  <a href="processing-planck-sources-with-hadoop_s1600_download.png" imageanchor="1" style="margin-left: 1em; margin-right: 1em;">
   <img border="0" src="processing-planck-sources-with-hadoop_s1600_download.png"/>
  </a>
 </div>
 <h2>
  Conclusion
 </h2>
 <div>
  The advantage of using Hadoop is mainly the scalability, this same setup could be used on AWS or Cloudera using hundreds of nodes. All the complexity of scaling is managed by Hadoop.
 </div>
 <div>
  The main concern is related to loading the data, in a HPC supercomputer it is easy to load directly from a high-performance shared disk, in a cloud environment instead we might opt for a similar setup loading data from S3, but the best would be to use Hadoop itself and stream the data to the mapper in the input files. This is complicated by the fact that Hadoop-streaming only supports text and not binary, the options would be either find a way to pack the binary data in a text file or use Hadoop-pipes instead of Hadoop-streaming.
 </div>
 <div>
  <br/>
 </div>
 <div class="separator" style="clear: both; text-align: center;">
  <br/>
 </div>
 <div class="separator" style="clear: both; text-align: center;">
  <br/>
 </div>
</div>
