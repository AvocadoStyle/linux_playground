#include <linux/module.h>
#include <linux/init.h>

static int __init hello_init(void) {
    pr_info(">>> Hello from the kernel!\n");
    return 0;
}

static void __exit hello_exit(void) {
    pr_info(">>> Goodbye from the kernel!\n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("You");
MODULE_DESCRIPTION("A simple Hello World kernel module");