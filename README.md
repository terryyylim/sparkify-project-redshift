# sparkify-project-redshift

## Content
* [Summary](#Summary)
* [ETL](#ETL)
* [Project structure](#Project-structure)
* [Installation](#Installation)

### Summary
This project involves the use of 2 AWS, [S3](https://aws.amazon.com/en/s3/) (Data storage)
and [Redshift](https://aws.amazon.com/en/redshift/) (Data warehouse with ``columnar storage``).

Data sources are provided by two public ``S3 buckets``. The first bucket contains information about songs and artists, while the second bucket contains simulated app activity logs by users. The objects contained in both buckets are JSON files. 

Since the JSON data objects for the event logs data don't correspond directly to the column names, we will use a JSONPaths file to map the JSON elements to columns. The order does not matter in the JSON source data, but the order of the JSONPaths file expressions must match the column order.
The COPY command is then used to access to the JSON files inside the S3 buckets and have their content copied onto the staging tables.

The STAR schema consist of the following fact and dimension tables.

#### Fact Table
`songplays`

#### Dimensions Table
`users`, `songs`, `artists`, `time`

#### Staging Table
`staging_events`, `staging_songs`

### ETL
The ETL (Extract-Transform-Load) process is relatively straightforward, with 3 main steps.
1. Run the `iac.ipynb` notebook, ensuring all necessary infrastructure is setup.
2. Run `create_tables.py` to create the relevant tables in the Redshift cluster generated in step 1.
3. Run `etl.py` to ;oad data from the public S3 buckets into Redshift tables and then insert data from staging tables to dimension and fact tables.

<b> Cluster Information: </b>
* A Redshift ``dc2.large`` cluster with <b> 4 nodes </b> has been created, with a cost of ``USD 0.25/h (on-demand option)`` per cluster
* [``IAM role ``](https://docs.aws.amazon.com/en_us/IAM/latest/UserGuide/id_roles.html) authorization mechanism, the only policy attached to this IAM will be am [``AmazonS3ReadOnlyAccess``](https://aws.amazon.com/en/blogs/security/organize-your-permissions-by-using-separate-managed-policies/)

Since the cost is on-demand, remember to shut it down after running through this example to prevent incurring unnecessary charges, since clusters can be easily spun up again.

### Project Structure
1. create_tables.py
* Contains helper functions which connects to the Redshift cluster and creates the necessary tables for insertion of data
2. etl.py
* Contains helper function which connects to the Redshift cluster and inserts the data from the S3 buckets 
3. sql_queries.py
* Contains schemas for the tables to be created when running create_tables.py
* Contains insertion, deletion and select queries for the songs, artists and simulated event log data stored in the S3 buckets
4. etl.ipynb
* Allows step-by-step running of IaC (Infrastructure-As-Code) process
5. dwh-example.cfg
* Example format for configurations required

### Installation
Clone this repository:
```
git clone https://github.com/terryyylim/sparkify-project-redshift.git
```

Change to sparkify directory
```
cd sparkify
```

To prevent complications to the global environment variables, I suggest creating a virtual environment for tracking and using the libraries required for the project.

1. Create and activate a virtual environment (run `pip3 install virtualenv` first if you don't have Python virtualenv installed):
```
virtualenv -p `which python3.6` venv
source venv/bin/activate
```

3. Install the requirements:
```
pip install -r requirements.txt
```