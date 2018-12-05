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

#define MY_WORK_QUEUE_NAME "WQsched.c"


int my_init(void);
void my_exit(void);
char translate_scan_code(int);


// static struct workqueue_struct *my_workqueue;

/*
* This will get called by the kernel as soon as it's safe
* to do everything normally allowed by kernel modules.
*/
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


    // a: 30,158
    // b: 48,176
    // c: 46,174
    // q: 16,144
    // w: 17,145
    printk("Interrupt handled scancode: %u", scancode);
    printk("Translated scan code: %c", translate_scan_code(scancode));


    // queue_work(my_workqueue, &task);

    return IRQ_HANDLED;
}

/*
* Initialize the module - register the IRQ handler
*/
int my_init()
{
    // my_workqueue = create_workqueue(MY_WORK_QUEUE_NAME);

    /*
    * Since the keyboard handler won't co-exist with another handler,
    * such as us, we have to disable it (free its IRQ) before we do
    * anything. Since we don't know where it is, there's no way to
    * reinstate it later - so the computer will have to be rebooted
    * when we're done.
    */
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
}

/*
* Cleanup
*/
void my_exit()
{
    /*
    * This is only here for completeness. It's totally irrelevant, since
    * we don't have a way to restore the normal keyboard interrupt so the
    * computer is completely useless and has to be rebooted.
    */
    free_irq(1, NULL);
}

/*
* some work_queue related functions are just available to GPL licensed Modules
*/
MODULE_LICENSE("GPL");
module_init(my_init);
module_exit(my_exit);



char translate_scan_code(int scancode)
{
    switch(scancode)
    {
        case 16: return 'q';
        case 17: return 'w';
        case 18: return 'e';
        case 19: return 'r';
        case 20: return 't';
        case 21: return 'y';
        case 22: return 'u';
        case 23: return 'i';
        case 24: return 'o';
        case 25: return 'p';
        case 30: return 'a';
        case 31: return 's';
        case 32: return 'd';
        case 33: return 'f';
        case 34: return 'g';
        case 35: return 'h';
        case 36: return 'j';
        case 37: return 'k';
        case 38: return 'l';
        case 44: return 'z';
        case 45: return 'x';
        case 46: return 'c';
        case 47: return 'v';
        case 48: return 'b';
        case 49: return 'n';
        case 50: return 'm';
        default: return '_';
    }
}