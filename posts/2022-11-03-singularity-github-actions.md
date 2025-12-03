---
categories:
- github-actions
- singularity
- ci
date: '2022-11-03'
layout: post
title: Build Singularity container on Github Actions

---

Github Actions runners are Ubuntu machines where we have `sudo` access, so we can install Singularity and build a container.

I have a repository with a working example: <https://github.com/zonca/singularity_github_ci>

In `.github/workflows/build_container.yml` we have the workflow definition.

First we install `Go` and `Singularity`:

```yaml
    - name: Install dependencies
      run: |
        sudo apt-get update && sudo apt-get install -y \
          build-essential \
          libssl-dev \
          uuid-dev \
          libgpgme11-dev \
          squashfs-tools \
          libseccomp-dev \
          pkg-config
    - name: Install Go
      uses: actions/setup-go@v2
      with:
        go-version: '1.13'
    - name: Install Singularity
      run: |
        export VERSION=3.7.0 && # adjust this as necessary \
        mkdir -p $GOPATH/src/github.com/sylabs && \
        cd $GOPATH/src/github.com/sylabs && \
        wget https://github.com/sylabs/singularity/releases/download/v${VERSION}/singularity-ce-${VERSION}.tar.gz && \
        tar -xzf singularity-ce-${VERSION}.tar.gz && \
        cd singularity-ce-${VERSION} && \
        ./mconfig && \
        make -C ./builddir && \
        sudo make -C ./builddir install
```

Then we can build the container:

```yaml
    - name: Build Container
      run: |
        sudo singularity build container.sif Singularity
```

Finally we can run the container to test it:

```yaml
    - name: Test Container
      run: |
        singularity exec container.sif python3 --version
```

See the logs of a successful run: (link removed as Github Action logs expire)
