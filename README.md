# Arango Performance Tester

Code to populate arangodb with large amounts of data and test query performance.
We're going to test latest arango version (3.3) using rocksdb backend.

## Setup

Ref: Arango Server Configuration:
https://docs.arangodb.com/3.3/Manual/Administration/Configuration/OperatingSystem.html

```bash
sudo bash -c "echo madvise >/sys/kernel/mm/transparent_hugepage/enabled"
sudo bash -c "echo madvise >/sys/kernel/mm/transparent_hugepage/defrag"
sudo bash -c "echo 2 >/proc/sys/vm/overcommit_memory"
sudo bash -c "echo 90 > /proc/sys/vm/overcommit_ratio"
sudo bash -c "echo 0 >/proc/sys/vm/zone_reclaim_mode"
sudo bash -c "sysctl -w 'vm.max_map_count=256000'"
export GLIBCXX_FORCE_NEW=1
```

### Arango Installation

Ref: https://www.arangodb.com/download-major/ubuntu/

```bash
curl -OL https://download.arangodb.com/arangodb33/xUbuntu_17.04/Release.key
sudo apt-key add - < Release.key
echo 'deb https://download.arangodb.com/arangodb33/xUbuntu_17.04/ /' | sudo tee /etc/apt/sources.list.d/arangodb.list
sudo apt-get install apt-transport-https
sudo apt-get update
sudo apt-get install arangodb3=3.3.17
```

Now create a database and optionally user for the testing.

### Cluster Setup

```bash
# on tf-api
arangodb --server.storage-engine=rocksdb --starter.address=10.131.78.29 \
         --starter.data-dir=./arango_data \
         --starter.join=arrangodb-4vcpu-8gb-ams3-01,arrangodb-4vcpu-8gb-ams3-02,arrangodb-4vcpu-8gb-ams3-03

# On tf-ar01
arangodb --starter.data-dir=./arango_data --starter.join 10.131.78.29

# On tf-ar02
arangodb --starter.data-dir=./arango_data --starter.join 10.131.78.29
```

### Code Setup


```bash
apt install python3-pip
pip3 install arango-orm
```

You can adjust the connection credentials in db_credentials.py

## Creating the Graph and Models

```bash
python3 main.py create_structure
```

## Populate the models

Inserting a million random records into the logs collection.

```bash
python3 insert_records.py populate logs 1000000
python3 insert_records.py populate areas 20000
python3 insert_records.py populate subjects 50000
python3 insert_records.py populate teachers 100000
python3 insert_records.py populate students 10000000
python3 insert_records.py populate teacher_areas 100000
python3 insert_records.py populate student_areas 10000000
python3 insert_records.py populate graph_connections 50000000
```


## Dump Stats

Dump size uncompressed: 34GB

### Records per collection

areas: 50,000
logs: 148,003,029
resides_in: 15,744,002
students: 10,000,000
studies: 6,497,555
subjects: 20,000
teachers: 100,000
teaches: 6,502,445

## Queries

### fetch 50 millionth record from collection

Example of an inefficient query:

```
for l in logs
    limit 5000000, 1
return l
```

Standalone Server: 16.310 s, Cluster: 15.852 s


### Fetch record by key.

Example of searching an indexed field. The record in question is 40 millionth
record in the logs collection:

```
for l in logs
    filter l._key=='07fa09bd-bd94-480a-8be0-7f129e5873a7'
return l
```

Standalone Server: 2.243 ms, Cluster: 3.963 ms


### Partial search on indexed field.

Example of performing partial search on indexed field:

```
for l in logs
    filter l._key like '8b4c%'
    limit 1
return l
```

Standalone Server: 210.867 ms, Cluster: 392.775 ms


### Partial search on non-indexed field.

Example of performing partial search on non-indexed field, fetching the 1000th
record where timestamp year is 2000:

```
for l in logs
    filter l.timestamp like '2000-%'
    limit 1000, 1
return l
```

Standalone Server: 60.900 ms, Cluster: 216.573 ms


## Graph Queries

### Select all teachers that reside in a particular area

Query:

```
WITH areas, teachers
FOR v, e, p IN 1..1 ANY 'areas/Area1000' GRAPH 'university_graph'
    FILTER v._key LIKE 'T%'
RETURN v
```

Total records found: 5

Standalone Server: 5.745 ms, Cluster: 487.283 ms


### Select all students that reside in a particular area

Query:

```
WITH areas, students
FOR v, e, p IN 1..1 ANY 'areas/Area1000' GRAPH 'university_graph'
    FILTER v._key LIKE 'S%'
RETURN v
```

Total records found: 194

Standalone Server: 4.752 ms, Cluster: 185.155 ms


### Get all students and teachers that either teach of study a subject

Query:

```
WITH students, teachers, subjects
FOR v, e, p IN 1..1 ANY 'subjects/3112' GRAPH 'university_graph'
RETURN p.vertices[1]
```

Total records found: 666

Standalone Server: 378.842 ms, Cluster: 455.717 ms


### Get all students that study any of the subjects that student S1000 studies

Query:

```
WITH students, teachers, subjects
FOR v, e, p IN 1..2 ANY 'students/S1000' GRAPH 'university_graph'
    FILTER p.edges[0]._id like 'studies%'
    AND p.edges[1]._id like 'studies%'
RETURN p.vertices[2]
```

Total records found: 324

Standalone Server: 556.032 ms, Cluster: 1.257 s
