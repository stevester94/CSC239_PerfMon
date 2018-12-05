#include <linux/kernel.h> /* We're doing kernel work */
#include <linux/module.h> /* Specifically, a module */
#include <linux/sched.h>
#include <linux/workqueue.h>
#include <linux/interrupt.h> /* We want an interrupt */
#include <linux/proc_fs.h>	/* Necessary because we use the proc fs */
#include <asm/io.h>
#include <linux/uaccess.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Robert W. Oliver II");
MODULE_DESCRIPTION("A simple example Linux module.");
MODULE_VERSION("0.01");

#define PROCFS_MAX_SIZE		1024
#define PROCFS_NAME 		"buffer1k"

#define MY_WORK_QUEUE_NAME "WQsched.c"


int my_init(void);
void my_exit(void);
char translate_scan_code(int);
ssize_t read_proc(struct file *filp,char *buf,size_t count,loff_t *offp);

// Proc vars 
int len,temp;
char *msg;



struct file_operations proc_fops = {
    read:   read_proc
};


// This is called when someone reads the proc file
/** @brief This function is called whenever device is being read from user space i.e. data is
 *  being sent from the device to the user. In this case is uses the copy_to_user() function to
 *  send the buffer string to the user and captures any errors.
 *  @param filep A pointer to a file object (defined in linux/fs.h)
 *  @param buffer The pointer to the buffer to which this function writes the data
 *  @param len Number of bytes attempted to be read
 *  @param offset Offset is where the file is being read from
 */
ssize_t read_proc(struct file *filp,char *buf,size_t count,loff_t *offp ) 
{
    printk("Count: %lu", count);
    if(count>temp)
    {
        count=temp;
    }
    temp=temp-count;

    copy_to_user(buf,msg, count);

    if(count==0)
        temp=len;   

    return count;
}



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

    proc_create("hello",0,NULL,&proc_fops);
    msg=" Hello World ";
    len=strlen(msg);
    temp=len;
    printk(KERN_INFO "1.len=%d",len);

    free_irq(1, NULL);
    return request_irq(1,           /* The number of the keyboard IRQ on PCs */
                       irq_handler, /* our handler */
                       IRQF_SHARED, "test_keyboard_irq_handler",
                       (void *)(irq_handler));




    return 0;
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

    return 0;
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