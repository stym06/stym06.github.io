---
title: Consistent Hashing
date: 2024-05-02
reading_time: 4 min read
---

The world works on distributed systems, and if there is one thing that is always happening is routing of requests. Be it how your Instagram posts go to that specific data-center or how the IPL matches being streamed are coming to us from which one of the global CDNs, all of this is a matter of effective choice of request->server mapping essentially.

We have load balancers which do some of this. They try to route the incoming requests to one of the available servers in many of the available algorithms. We have distributed clusters of databases and servers all trying to do the same thing.

Wonder what they are using?

Consistent Hashing.

Wait, what's Hashing, first of all, and Consistent at that?

Let's dive in!

Let's say you have a bunch of keys you want to store and retrieve and you have a bunch of servers as well. For consistency, let's assume we have 10 keys and only 3 servers

We can store these keys randomly, but we won't be able to deterministically say which one of the server did my key go to, right? Ok, so we can store them in a round-robin fashion, sounds cool? Or cooler, we can encode the data into 8-bit and take the modulo of 3, so that we get a number betwen [1 -> 3], which gives us a server name. And since the encoding is also fixed, on retrieval of the key, we can again encode it, get the server name and do a fetch request for our key.

All fun till now. This works, Yes.

But imagine, if Server-2 goes down. We will have to move all our keys to one of the remaining ones, right? Or let's say someone else also wants to send keys, we might need to add more servers. Well, for uniformity, we would need to relocate most of our keys to this new shiny server.

Turns out this data movement operation will take all the time when doing upscaling and downnscaling. What's a better way then?

Enter Consistent Hashing!

Here, we dont do the modulo thing to get the server id, but what we do is have a giant hash space where our servers reside with their hashkeys. And now, not taking the hash-collision approach of going to the index, we hash our key, and take a stroll to the right to find the first available hash. If we find it, that's our server!

![Consistent Hashing Sample Illustration](https://upload.wikimedia.org/wikipedia/commons/7/71/Consistent_Hashing_Sample_Illustration.png)

Let's implement this.

One way to implement this is using arrays and going to the right side of the array, but that takes O(n) in the worst case, so we just create a Sorted Map.

```java
public class ConsistentHashing {

    private final MessageDigest md;
    private final TreeMap<Long, String> circle;
    private final int numReplicas;

    public ConsistentHashing(int numReplicas) throws NoSuchAlgorithmException {
        this.numReplicas = numReplicas;
        this.md = MessageDigest.getInstance("SHA-256");
        this.circle = new TreeMap<>();
    }

    public void addServer(String key) {
        for(int i = 0; i < numReplicas; i++) {
            Long hash = generateHash(key + i);
            circle.put(hash, key);
        }
    }

    public void removeServer(String key) throws Exception {
        for(int i = 0; i < numReplicas; i++) {
            Long hash = generateHash(key + i);
            circle.remove(hash);
        }
    }

    public String getServer(String key) throws Exception {
        Long hash = generateHash(key);
        SortedMap<Long, String> tailMap = circle.tailMap(hash);
        Long firstServerTotheRightKey = tailMap.isEmpty() ? circle.firstKey() : tailMap.firstKey();
        return circle.get(firstServerTotheRightKey);
    }

    private long generateHash(String key) {
        md.reset();
        md.update(key.getBytes());
        byte[] digest = md.digest();
        long hash = ((long) (digest[3] & 0xFF) << 24) |
                ((long) (digest[2] & 0xFF) << 16) |
                ((long) (digest[1] & 0xFF) << 8) |
                ((long) (digest[0] & 0xFF));
        return hash;
    }

    public static void main(String[] args) throws Exception {
        ConsistentHashing consistentHashing = new ConsistentHashing(10);

        //add servers and keys
        final List<String> servers = List.of("s1", "s2", "s3", "s4", "s5");

        for(String server: servers) {
            consistentHashing.addServer(server);
        }

        //key for k1
        System.out.println("Current location of k1 is " + consistentHashing.getServer("k1"));

        //remove server s5
        System.out.println("Removing server s5");
        consistentHashing.removeServer("s5");

        //key for k1
        System.out.println("New location of k1 is " + consistentHashing.getServer("k1"));
    }
}
```
