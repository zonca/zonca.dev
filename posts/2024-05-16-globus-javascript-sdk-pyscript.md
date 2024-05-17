---
categories:
- python
date: '2024-05-16'
layout: post
title: Load data from Globus in the browser and plot with pyscript

---

Globus supports a [Javascript SDK](https://github.com/globus/globus-sdk-javascript) which allows to authenticate against Globus Auth and then access all the Globus services, for example accessing protected data or setting up transfers between endpoints.

I think the project is really powerful because brings Globus to the browser, however it is sparsely documented, so it is really difficult to leverage its potential.

This is somehow related to my work on the [CMB-S4 data portal](https://data.cmb-s4.org/about.html), the idea is that on top of the static Catalog inside a Data Portal we could also provide additional services via Javascript, without the need of a backend server.

For example plotting a dataset which requires authentication.

Rick Wagner created an example that uses the Globus Javascript SDK to authenticate and retrieve a protected JSON dataset and plot it with `Chart.js`, see <https://rpwagner.github.io/globus-sdk-javascript-ex-01/>.

I expanded the example by passing the JSON dataset to [PyScript](https://pyscript.net/) (Python running in the browser) and then using `pandas` capabilities to parse the JSON into a DataFrame and create a Histogram on the page.

* [Webpage with Globus and PyScript](https://zonca.github.io/globus-sdk-javascript-ex-01/)
* [Github repository](https://github.com/zonca/globus-sdk-javascript-ex-01)
* If you would like to reproduce this, follow the instructions [on the Globus Javascript SDK Basic example to create a Globus app](https://github.com/globus/globus-sdk-javascript/tree/main/examples/basic)

A few notes on the implementation:

* I was not able to use `pydom` in PyScript to make visible the iframe with the code, so I used Javascript for that
* The HTTP request to load the data is automatically launched just after signing in, when completed, the "Plot data" button is activated
* I didn't find a way to call the Python function `pandas_plot` from Javascript, that is why I added the "Plot data" button
* I directly pass the JSON string to Python, then use `pandas.read_json` to parse it
* Impressive how you can quickly load a huge package like `pandas` inside the browser, it is overkill for this example, but could be handy
