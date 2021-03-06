## Redis 中的事务
   在我们平常的程序中，不是多个客户端同时处理数据时，程序都会稳定的执行，但是我们都会遇到多个客户端访问的情况，这样就会容易出现数据错误的情况。为了防止这个情况我们才有了事务这一说。那么什么是事务呢？
   1. 事务是一个单独的隔离操作：事务中的命令都会序列化、按照顺讯的执行，并在在执行过程找那个不会被其他客户端发送过来的命令所打断。
   2. 事务是原子性的操作，命令要么是全部执行，要么是全部都不执行。
### 使用事务
   为了方便我们在程序中使用Redis的事务，在Redis中有一个EXEC命令来帮忙除服并执行事务中的所有执行。在客户端开启事务之后如果因为网络的原因断线导致没有成功的执行exec，那事务中的所有命令都不会被执行。另一方面客户端成功执行exec命令后，事务中的所有命令都会执行。
   Redis有可能会出现一种事务错误的情况。当我们采用AOF做数据的持久化，在redis中是采用单个的write命令将事务写入到磁盘中。如果redis服务挂掉导致部分事务命令写入到磁盘中 在启动的时候会汇报错误。
   怎么使用事务请参考以下命令：
```
  >mutl
 >set key value
 >set key1 value
>exec
```
   我们使用这个事务，在exec命令中的回复其实是一个数组，数据中的每个元素 都是执行十五中命令产生的回复。并且顺序也是一致的。当客户端处于事务状态时，所有命令都会返回一个QUEUED的状态回复，这些入队命令将在exec中调用时执行。
### 出现的错误
在事务执行的时候，我们可能会遇到下面两种错误：
1. 事务执行之前出现的错误：比如命令错误，语法错误，内存不足等异常
2. 调用之后出现的错误： 比如将列表命令用在了字符串键上面。

那么我们在出现这些异常的时候Redis是怎么解决这个问题的呢。在我们前面说过，Redis在mutl中执行会返回一组数组，并且每个命令都会返回QUEUED的回复，这个代表的是成功，相反 入队失败，大部分客户端就会取消这个事务了。但是Redis的版本不同，情况也不同，在2.6.5以后失败会进行记录，在以前的版本会直接忽略入队失败的命令。
在我们使用redis之前，使用mysql关系型数据库，同样也会使用事务，但是mysql中的事务是会支持数据回滚的，而mysql中却不支持，这是为什么呢？那是因为在Redis中命令只会因为错误的语法失败或者错误的类型键上失败，这就意味错误是在编程阶段造成的，并且不支持回滚，Redis的内部可以保持简单且快速的方式访问。
### 使用check-and-set命令实现乐观锁和watch命令观察
watch命令用来帮助我们为Redis事务提供check-and-set 行为。watch是通过观察整个事务中这些被操作的键是否被改动来达到监视的行为的。如果至少一个键在执行exec之前被改动过，那么整个事务会被取消，并且返回nil-reply 表示事务失败。watch可以监视多个键 比如这样的watch key key key . 

在我们使用数据的库的时候，经常会用到主从同步的功能，一般都是主库用来插入数据，从库用来读取数据，减少数据库的读取和插入的压力。并且我们在Redis中也看到了这种技术的应用主从复制。主master 与从slave
Redis在复制中主要是依靠了三个主要的机制：
1. master实例与slave实例链接正常的时候，master会发送一连串的命令流来保湿对slave的更新，以便于将自身的数据集的改变复制给slave。
2. 当master与slave链接端开之后么因为网络问题或者是主从意识到连接超时，slave重新链接master进行部分充同步，这意味着他只是会尝试获取在断开连接期间丢失的命令流
3. 当无法进行部分重同步时，slave会请求进行全量数据重同步，master需要创建所有的数据快照，将之发给slave,之后再数据集更改时持续发送命令到slave。
## Redis的复制
在Redis中，默认使用的是异步复制的方式，特点是高延迟和高性能。 这是绝大多数Redis用例的自然复制模式，但是Redis服务器会一步的确认其从主Redis服务器周期接收到的数据量。但是我们在使用Redis的时候也可以用使用WAIT的命令来请求同步复制某些特定的数据。
1. Redis使用异步复制。slave和master之间异步的确认处理的数据量
2. 一个master可以有多个slave。
3. slave可以接受其他slave的链接。除了多个slave可以链接同一个master之外，还可以像层叠状的结构连接到其他slave 。从Redis4.0开始 所有的sub-slave将从master接收到同样的复制 。
4. Redis的复制在master侧是非阻塞的。这意味着master在一个或多个slave记性初次同步或者是部分重同步的时候还可以接受查询请求。
5. 复制在slave侧也是非阻塞的。
6. 复制既可以被用在可伸缩性方便多个slave记性，或者仅用于数据安全 。
7. 可以使用复制避免master将全部数据写入磁盘造成的开销，一种典型的技术是配置master避免对磁盘的持久化没然后链接一个slave其配置成不定期保存或者开启aof.然而重新启动的master程序姜葱一个空数据集开始，当slvae 试图同步的时候 slave也会被清空
### 复制的安全性
我们在使用复制的功能的时候，应该在两者都开启持久化，如果不能启动，那么也应该配置实例来避免重置后自动重启。如果我们没有持久化当master出现问题的时候，那么其他从节点从master复制就会把自身的数据清空，造成从节点数据也丢失。
### 复制如何工作的
在redis的master中都有一个replication ID ,这是一个较大的伪随机字符串，标记了一个给定的数据集。每个master都有一个偏移量，master将自己产生的复制刘发送给slave时，发送多少个自己的数据，自身的偏移量就会增加多少。目的是为了有新的操作时，修改自己的数据集并且以这个来更新slave的状态。在Redis的复制过程中全量的重同步要求在磁盘上创建一个RDB文件，然后将它从磁盘加载到内存中，然后slave以此进行数据同步。如果磁盘性能很低的情况下这对于master就是一个压力很大的操作。Redis在2.8.18版本后支持无磁盘的复制版本。子进程直接发送RDB文件给slave.无需使用磁盘作为中间存储介质。
### 配置Redis的复制
在Redis中配置复制功能还是很方便的，在slave的配置文件加上 slaveof master port  内容。但是我们也说了我们可以使用无磁盘复制，那么我们就需要配置 repl-diskless-sync的相关参数 。详细信息可以看redis.conf
### 只读性质的slave
在Redis2.6以后 slvve支持 只读模式且默认开启。redis.conf的slave-read-only变量控制这个行为，且可以在运行时使用CONFIG SET来随时开启或者关闭。在只读的模式下拒绝所有写入的命令，我们在redis.conf中的使用rename-command 指令可以禁用上述管理员命令以提高只读的安全性。在Redis的2.8版本以后我们可以拥有N个slave链接到master 时，配置的master才有可能接收写查询。在复制的过程中，无法确保slave是否实际接收到给定的写命令。因此总会有一个数据丢失窗口。原理如下：
1. Redis slave每秒钟都会ping master ,确认已处理的复制流的数量。
2. Redis master 会记得上一次从每个slave 都收到ping的时间。
3. 用户可以配置一个最小的slave数量，使得它滞后<= 最大秒数。如果有N个slave ,那么滞后小于M秒 则写入将被接收。
然而在这些情况下 redis还有可能出现写入错误的情况，那么当错误时 master会回复一个error并且写入将不被接收。这个特性有两个参数
- min-slaves-to-write<slave数量>
- min-slaves-max-lag<秒数>
### Redis复制处理key的过期
平常程序中，我们会有一些需求就是需要设置key的过期时间，让key在规定的时间内自然的消失，不需要程序再去执行删除操作。那么我们就可以使用Redis的过期机制来限制key的生存时间。Redis中为了实现这样的功能，没有采用同步时钟的功能，而是使用了另外的三中方式：
1. slave不会让key过期，而是等待master让key过期。当master让key过期后，会发送一个DEL命令并传输到slave中。
2. 如果上面的方式无法执行的时候，或者有延时的可能性的话，slave只能使用它的逻辑时钟报告只有在不违反数据的一致性读取操作的中存在的key。这样slave避免报告过期的key仍然存在。
3. 在Lua脚本执行的时候，Redis不会执行任何的key过期操作，停止运行，master中的时间是被冻结的。所以在Lua脚本运行期间 key要么不存在，还防止key在脚本中间过期。并且将相同的的脚本发送到slave中。从而在两者的数据集中产生相同的效果。
4. 一旦一个slave被提升为master ,它将开始独立的过期key，而不需要旧的master帮助。
![琪琪基地](https://upload-images.jianshu.io/upload_images/4237685-1f7fce30b38ed563.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

 




