#include <linux/kernel.h> /* We're doing kernel work */
#include <linux/module.h> /* Specifically, a module */
#include <linux/sched.h>
#include <linux/workqueue.h>
#include <linux/interrupt.h> /* We want an interrupt */
#include <asm/io.h>


MODULE_LICENSE("GPL");
MODULE_AUTHOR("Robert W. Oliver II");
MODULE_DESCRIPTION("A simple example Linux module.");
MODULE_VERSION("0.01");


static void got_char(void *scancode)
{
    printk(KERN_INFO "Scan Code %x %s.\n",
    (int)*((char *)scancode) & 0x7F,
    *((char *)scancode) & 0x80 ? "Released" : "Pressed");
}

/*
* This function services keyboard interrupts. It reads the relevant
* information from the keyboard and then puts the non time critical
* part into the work queue. This will be run when the kernel considers it safe.
*/
irqreturn_t irq_handler(int irq, void *dev_id)
{
    /*
    * This variables are static because they need to be
    * accessible (through pointers) to the bottom half routine.
    */
    static int initialised = 0;
    static unsigned char scancode;
    static struct work_struct task;
    unsigned char status;

    /*
    * Read keyboard status
    */
    status = inb(0x64);
    scancode = inb(0x60);

    // if (initialised == 0) {
    //     INIT_WORK(&task, got_char, &scancode);
    //     initialised = 1;
    // } else {
    //     PREPARE_WORK(&task, got_char, &scancode);
    // }

    printk("Interrupt handled: %u", scancode);

    // queue_work(my_workqueue, &task);

    return IRQ_HANDLED;
}


static int __init lkm_example_init(void) {
 printk("Hello");

    free_irq(1, NULL);

    /*
    * Request IRQ 1, the keyboard IRQ, to go to our irq_handler.
    * SA_SHIRQ means we're willing to have othe handlers on this IRQ.
    * SA_INTERRUPT can be used to make the handler into a fast interrupt.
    */
    return request_irq(1,           /* The number of the keyboard IRQ on PCs */
                       irq_handler, /* our handler */
                       IRQF_SHARED, "test_keyboard_irq_handler",
                       (void *)(irq_handler));


 return 0;
}
static void __exit lkm_example_exit(void) {
 printk("Hello");
}


module_init(lkm_example_init);
module_exit(lkm_example_exit);
