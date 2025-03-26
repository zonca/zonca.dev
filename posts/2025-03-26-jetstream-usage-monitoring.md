---
categories:
- jetstream2
date: '2025-03-26'
layout: post
title: Jetstream2 Usage Monitoring
slug: jetstream2-usage-monitoring
---

## Introduction

Monitoring resource usage on cloud platforms is essential for managing allocations effectively. For users of Jetstream2, the Unidata team has developed a useful script to track Service Unit (SU) consumption over time.

## Jetstream2 Usage Monitoring Script

The script is available in the [Unidata Science Gateway repository](https://github.com/Unidata/science-gateway/blob/master/openstack/bin/usage-monitoring/usage_monitoring.py) and provides several useful features for Jetstream2 users.

### Features

This Python script allows you to:

* Generate an OpenStack token for authentication
* Use this token to query the Jetstream2 Accounting API
* Parse the output to get your current amount of used SUs
* Save usage data to a CSV file for record-keeping
* Create a plot visualizing your usage over time
* Perform a simple linear analysis to determine your usage rate and make predictions about future SU consumption

### How It Works

The script interfaces with the Jetstream2 Accounting API to retrieve allocation and usage data. It then processes this data to provide insights into how quickly you're consuming your allocation, helping you plan and manage your resources more effectively.

### Getting Started

To use this tool, you'll need to:

1. Clone the repository
2. Install the required dependencies
3. Configure your OpenStack credentials
4. Run the script to begin monitoring your usage

This is particularly useful for projects with fixed allocations that need to track and predict their resource consumption over time.

## Conclusion

For researchers and developers using Jetstream2, this monitoring tool provides a simple yet effective way to keep track of SU usage, helping to avoid unexpected allocation exhaustion and enabling better resource planning.