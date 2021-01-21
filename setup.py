import setuptools
import versioneer

with open("README.rst", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

setuptools.setup(
    name="dask-ctl",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Jacob Tomlinson",
    author_email="jacob@tomlinson.email",
    description="A set of tools to provide a control plane for managing the lifecycle of Dask clusters.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points="""
        [console_scripts]
        daskctl=dask_ctl.cli:daskctl
        [dask_cluster_discovery]
        proxycluster=dask_ctl.proxy:discover
      """,
)
