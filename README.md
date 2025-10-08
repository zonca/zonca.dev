# Singularity Dask Zarr Container

This repository provides a Singularity container designed for scientific computing tasks, specifically leveraging Dask and Zarr for efficient data processing and storage.

## Getting Started

### Prerequisites

*   Singularity (or Apptainer) installed on your system.

### Building the Container

To build the Singularity image (`singularity_dask_zarr.sif`), navigate to the root of this repository and run the following command:

```bash
make build
```

This command uses the `Singularity.def` definition file to create the container, installing all necessary Python dependencies listed in `requirements.txt` via Miniconda.

### Testing the Container

After building, you can verify the container's functionality by running the test command:

```bash
make test
```

This will execute a Python script inside the container to confirm that Dask and Zarr are correctly installed and accessible, printing their versions.

## Project Structure

*   `Singularity.def`: Defines the Singularity container image, including the base OS, dependencies, and environment setup.
*   `requirements.txt`: Lists the Python packages (e.g., Dask, Zarr, NumPy, Xarray) that will be installed in the container.
*   `Makefile`: Provides convenient commands for building and testing the Singularity container.
