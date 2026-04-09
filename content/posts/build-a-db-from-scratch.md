---
title: Building a Database From Scratch
date: 2024-07-11
reading_time: 4 min read
---

Hey folks,
This is the introductory chapter on a series of blogs on how you can build a database from scratch by yourself.

But Why? Why build a database, you ask? There's plenty already. And I only care about the CRUD stuff.

> Umm, I guess most of us treat a database as a black box and dump stuff into it. But we only care about some of it if we get a connection pool failure alert on our pager. We dig a bit and then tune it to fix it there. But, to really make the most of your database and most importantly the way you decide if the task requires you to use a SQL or NoSQL one, you gotta see what's the real difference in the two.

This can only happen if you have built one.

## Some Background

I've always wanted to learn how a database actually works under the hood. Two things really intrigued me:

1. What the actual `INSERT` command does. I assumed it must finally be doing some sort of a `file.Write()` somewhere.
2. Why are there so many databases out there. What's the fight about SQL vs NoSQL vs Columnar Storage vs KV store. What's the actual difference between an OLTP and an OLAP.

I finally decided to dig deep into the internals of it, and bought two books:

- *Designing Data-Intensive Applications* by Martin Kleppmann: https://www.oreilly.com/library/view/designing-data-intensive-applications/9781491903063/
- *Database Internals* by Alex Petrov: https://www.oreilly.com/library/view/database-internals/9781492040330/

Watched a lot of CMU videos: https://www.youtube.com/watch?v=df-l2PxUidI&list=PLSE8ODhjZXjaKScG3l0nuOiDTTqpfnWFf&index=3&ab_channel=CMUDatabaseGroup

But at one point, when I started getting bored with the theory, I put my foot down and decided to build one.

How hard could it be, I thought! Well, very much!

The rest of this article is about what really goes inside building a database system. There are a lot of moving parts, all of which work in harmony with each other to finally give you that simple API of `db.put(<key>, <value>)`.

Let's see the components of the most popular database, `MySQL`:

![MySQL Architecture](https://i.ytimg.com/vi/Szr4DrM4E8Q/sddefault.jpg)

Looking at it, we have the following components:

1. DB Connectors/Client
2. SQL Interface API
3. SQL Parser
4. Query Optimizer
5. Buffer Pools
6. Storage Engines (InnoDB, MyRocks, MyISAM)
7. File System

That's a lot of things under the hood, each with their own share of complexity.

I decided to break this down in a bottom-up fashion, and decided to first understand how the actual data is stored in the end. It must be something, right? Some sort of array maybe or a hashmap or some kind of data structure, right? But how do you store that on a file??

Thing is, you need a disk-backed data structure to efficiently store data on disk. And all of us mostly use the in-memory structures like BSTs, Hashmaps, Sets. That stuff is not really meant for disk usage because of a lot of reasons!

Since you got to have your database the fastest component in your system, because at the end of it, your API is going to call the database to store/retrieve, you need to use some DS that allows you to store data efficiently so that further reads can make the most of it.

There are some pre-requisites and theory/primer that you need to understand to move forward. I have attached some references for you to look at:

1. How Disks work (HDDs, SSDs)
2. Understand disk-access patterns. Mainly, why Sequential i/o is better than random i/o
3. Handling power failures to have Integrity semantics
4. Disk-based data structures like B-Tree, B+ Trees, LSM
5. Understanding Pages and Blocks at the OS level.
6. File Formats (CSV, Parquet, etc). Essentially, Encoding and Compression techniques

Now that we know a bit about everything, we can dig into the code of the most famous database on the planet: *SQLite*

Here's a reader-friendly version to analyse parts of it: https://github.com/davideuler/SQLite-2.5.0-for-code-reading

I have worked with Maxwell/Debezium, which are tools that let you replicate databases. I thought, where else to start than reading about this binlog stuff itself.

Wait, what's this `Binlog`?

Essentially, when you issue any query to a database, the engine first writes the command that it is going to do on a structure append-only log file. Then it issues the command (SELECT/INSERT or any command). It does so to have `I` (Integrity) in the `ACID` that it guarantees.

In case the db operation, let's say the INSERT fails for some reason, because of disk corruption or power failures or data center floodings, it can replay the action by reading from the log file that it had previously written to.

This is what we call in database terms, a `Write-Ahead-Log (WAL)` mechanism.

Here's some Postgres theory on it: https://www.postgresql.org/docs/current/wal-intro.html

I took the liberty to write this on my own:

Here's my naive implementation of a WAL: https://github.com/stym06/rebuf
And the accompanying HN post: https://news.ycombinator.com/item?id=40908178

I wrote this to understand how a simple thing like logging can be so complex, and can be so thoughtfully built.

The next blog will be a deep dive on the actual implementation of the WAL.

Till then, Bye.

Stay Curious!
