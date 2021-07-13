# Star Wars Client

This project allows users to explore Star Wars data from 
[swapi](https://github.com/phalt/swapi) in a meaningful way.

## Requirements

* Python 3.6+

## Installation

Clone the repository:

```shell
git clone https://github.com/potasiak/starwars.git && cd starwars
```

Create a virtual environment (whichever you like the most, I like 
`virtualenvwrapper`):

```shell
mkvirtualenv -p "$(which python3)" starwars-client
```

Install requirements:

```shell
pip install -r requirements.txt
```

Run migrations:

```shell
python manage.py migrate
```

Run a development server:

```shell
python manage.py runserver
```

The website should be available at [localhost:8000](http://localhost:8000/).

### Running tests

I like to use `pytest` due to its simplicity.

```shell
pytest
```

You can also run tests with coverage:

```shell
pytest --cov=starwars
```

## Usage

I described what you can do in the application in case anyone needs it.

If you're more interested in possible further improvements in the application,
scroll down.

### Index

The index page contains a list of downloaded datasets. You can download 
a dataset by clicking the "Fetch dataset" button.

Each dataset can be opened for exploration.

### Fetch dataset

When clicking the "Fetch dataset" button, a new dataset is downloaded and saved
in the system. It might take couple seconds, as it's implemented directly in 
the view.

Data from the API is fetched lazily as `petl` iterates over it, so memory should
not be an issue - garbage collector should manage to handle it.

You will get a message about successful (or failed) download with a link to
the dataset's details, and a total time it took to fetch it.

### Dataset details

When you open a dataset, you will see its UUID, date when it was fetched and
its data.

The "Count values by" row lets you select columns to count values for. It 
results in aggregation of all data in the dataset by the selected columns.
The buttons are toggleable.

The data table contains all the data from the dataset or its aggregations. You
can sort it by a selected column. Click once for ascending sort and twice for 
descending sort.

Below the table there is a "Show more" button. Click it to reveal more data.
It will show 10 more rows each time you click on it.

## Further improvements

The application is obviously very far from ideal, but the implementation is 
rather good-enough for its purpose. There is a lot of space for improvements:

1. Instead of downloading data directly in a view, it should be done 
   concurrently. The bare minimum for that purpose would be use of **asyncio**
   to improve CPU utilization on I/O-bound operations (since `requests` is used,
   it might be a good idea to use `grequests` or `requests-futures`). Ideally,
   it should be also moved to an external worker through a message queue. 
   **Celery** would be a good choice for that purpose.
   
2. On loading the data from the CSV files, it would also be a good idea to use
   **asyncio**. Without it, when many users would try to explore the same 
   dataset, they might except high latency due to CPU waiting for I/O-bound
   operations.
   
3. There could be **more thorough tests**. Current test coverage is 78%.
   The views are not tested at all, and other functions are tested only for 
   basic cases. Because of a limited time, it could not be done better.
   
4. It's hard to decide on **system's architecture** when it's purpose is not 
   clear. Obviously, it's just a sample application, so there was nothing 
   I could've done. The functions are scattered around the code base
   in a somewhat coherent structure, just like in most of Django boilerplate 
   applications. Complex applications for commercial use should not be done in
   this manner unless the timeline is really tight, or the application is 
   supposed to be short-lived.
   
5. It's my first time using **petl**, so I might have not used it in the best 
   possible way. The result you see is what I figured out should be done based
   on the official documentation, and I'm quite satisfied with the result. Tried
   my best to separate ETL stages to make them independent of each other.
   
6. There should be **better handling of exceptions**. For example, in 
   the `fetch` view I'm catching `Exception` which is not a good practice, 
   especially since I put exception messages in the response (it's a security 
   issue). Better exception handling would require more thorough tests (see #1)
   to discover as many exceptions as possible. Each exception might need to be
   handled differently, and should give the user an information about what 
   happened in a way they would understand (without technical details and 
   potentially sensitive information).
   
7. The **CSV files could be stored in an external storage**, like **AWS S3**. 
   Storing files on the same machine that runs the application (especially when 
   it's dockerized or in any other way temporary) is not a good idea. It would 
   obviously increase the read time due to network latency, but given 
   the application would also run in the same AWS region, on the same VPC, it 
   wouldn't be noticeable for users. 

8. Before the application would be ready for production, the settings should be
   carefully crafted to ensure maximum security. The project uses the standard
   Django settings, split into development and testing. 

Other things that should be done in (almost) every commercial project:

* containerization (e.g. Docker + docker-compose)
* CI/CD pipelines that at least test the application before merging any changes
* infrastructure (IaaC would be best - Ansible, Terraform, Packer, etc.):
   * virtual machine images or ECS / EKS configuration
   * HTTP server configuration (e.g. nginx + gunicorn) + high-availability (e.g. 
     HAProxy)
   * database configuration (e.g. MongoDB or PostgreSQL)
   * other cloud-related operations
