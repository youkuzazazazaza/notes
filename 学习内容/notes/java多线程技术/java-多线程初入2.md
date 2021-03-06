该文章接着上篇来写如果读者感觉突入，需要把上篇多线程初入1看下。
如有不对的地方，请指出，大家互相交流。本文内容大部分摘自实战java高并发程序设计该书
#### 并行的两个定律
1. 获得更好的性能。 一般我们会把串行的程序改成并行的 期望提高的程序执行效率 问题。
2. 业务的需要。 
3. 两个定律分别为 Amdahl 和 Gustafson 
 - Amdahl 定律 定义是 加速比 = 优化前的系统耗时 / 优化后系统耗时。
加速比的比值越大那么优化效果越好。

![公式推导](http://upload-images.jianshu.io/upload_images/4237685-1f3ff7577522bd7f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
如图所示，F 代表的是串行比例， n代表的是n个处理器，Tn代表的是处理器优化后的耗时，F是程序中只能串行的比例。最终看到当n越大时 那么 加速比与串行率成反比。但是如果我们就一直只增加处理器的数量 那么后期处理增加 提高的程序性能，不能有很大 的提升。我们还应该修改程序中串行的比例 这样才能用最小的代价换取最大的加速比
- Gustafson 加速比定义是一样的 ，但是这两者处理的角度不一样。

![Gustafson](http://upload-images.jianshu.io/upload_images/4237685-2c108b78e0589f55.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
这个理论最后的结果是在串行比例很小的时候 加速比基本上就是处理的核数。
两个理论都有自己的关注点，关注点不同导致结果不同。矛盾并不存在。
#### java的JMM 中的原子性、可见性、有序性
1. 原子性  是指一个操作是不可中断的 。即使是多个线程一起执行的时候，一个线程一旦开始，就不会被其他线程干扰。  保证原子性 就是线程运行 不会被其他线程干扰 ，该线程中的内容也不被其他线程所影响 修改。
2. 可见性  就是指 当一个线程修改了某一个共享变量的值，其他线程就能立即知道该变量被修改了。 在多线程中 全局变量可能 将变量值缓存在cache 中或者在寄存器中那么，某个修成修改了值 ，可能其他线程不能立即知道 该变量的修改。那么其他线程就会出现问题。
3. 有序性  如果在串行上来说，有序性会按照顺序执行，但是在多线程中***可能***会出现执行 的时候 进行 指令重排的情况 。串行指令重排能导致语义一致，但是多线程的时候***可能***保证不了了
####  指令不能进行重排 : Happen-Before 规则


![指令重排规则](http://upload-images.jianshu.io/upload_images/4237685-257f1b58fb6795fb.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

