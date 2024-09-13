# Infusion

A CLI tool for generating documentation for source code using advanced language models.

## Table of Contents
- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Practical example](#practical-example)
- [Options](#options)
- [Features](#features)
- [License](#license)

## Description

Infusion is a command-line tool designed to assist developers by generating documentation for their source code. By providing file paths, Infusion leverages language models like OpenAI’s GPT to modify the files by inserting appropriate comments and documentation. The tool supports multiple programming languages.

It is particularly useful when you need structured comments (e.g., JSDoc for JavaScript/TypeScript or JavaDoc for Java) or simple comments above functions and classes. Infusion saves the modified files to a specified output directory.

## Installation

To install and run Infusion locally, clone the GitHub repository.

```bash
git clone https://github.com/your-username/infusion.git
cd infusion
```

After that, you will have to set up a virtual environment and install all the dependencies. 

If you are on Windows, use **PowerShell** to set up virtual environemnt using the command:
```powershell
./setup/setup.ps1
```

If you are on Mac / Linux, use the following command:
```bash
./setup/setup.sh
```

After you are done setting up virtual environment, you need to open it. You do this using the following command:
```bash
pipenv bash
```

Once you are in the virtual environment, you can start using the **Infusion** utility. Read [this](#usage) section for usage. 

Once you are done using the utility, you can exit the virtual environment by running:
```bash
exit
```

## Usage

To use Infusion, run the following command, replacing FILE_PATHS with the paths to the source code files you want to process:
```bash
python -m src.app [OPTIONS] [FILE_PATHS]
```

## Examples

Process a single file:
```bash
python -m src.app ./path/to/source.py
```

Process multiple files and specify an output folder:
```bash
python -m src.app ./file1.js ./file2.py --output my_output_folder
```

## Practical example

Let's say we have a Java file with some source code `Program.java`:
```java
import java.util.*;
import java.util.concurrent.*;

public class TaskScheduler {
    
    private final ScheduledExecutorService executorService;
    private final Map<String, ScheduledFuture<?>> scheduledTasks;

    public TaskScheduler(int poolSize) {
        this.executorService = Executors.newScheduledThreadPool(poolSize);
        this.scheduledTasks = new ConcurrentHashMap<>();
    }

    public void scheduleTask(String taskId, Runnable task, long initialDelay, long period, TimeUnit unit) {
        if (scheduledTasks.containsKey(taskId)) {
            throw new IllegalArgumentException("Task with ID " + taskId + " is already scheduled.");
        }
        ScheduledFuture<?> scheduledTask = executorService.scheduleAtFixedRate(task, initialDelay, period, unit);
        scheduledTasks.put(taskId, scheduledTask);
    }

    public boolean cancelTask(String taskId) {
        ScheduledFuture<?> scheduledTask = scheduledTasks.remove(taskId);
        if (scheduledTask != null) {
            return scheduledTask.cancel(false);
        }
        return false;
    }

    public void rescheduleTask(String taskId, Runnable task, long initialDelay, long period, TimeUnit unit) {
        cancelTask(taskId);
        scheduleTask(taskId, task, initialDelay, period, unit);
    }

    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
                if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {
                    System.err.println("Executor did not terminate");
                }
            }
        } catch (InterruptedException ie) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    public static void main(String[] args) {
        TaskScheduler scheduler = new TaskScheduler(2);
        Runnable task = () -> System.out.println("Task executed at " + new Date());

        scheduler.scheduleTask("task1", task, 0, 5, TimeUnit.SECONDS);

        try {
            Thread.sleep(15000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        scheduler.cancelTask("task1");
        scheduler.shutdown();
    }
}
```
Let's provide absolute path to this file using our tool.
```bash
python -m src.app C:\\Users\\andri\\Desktop\\examples\\Program.java
```

We will be asked to provide our `openAI` API key:
```bash
Open AI API key:
```
It won't be seen for security purposes.

After we have entered it, the processing will begin, and after a few seconds we will have `fusion_output` folder containing `Program.java` file with added comments:
```java
import java.util.*;
import java.util.concurrent.*;

/**
 * The class TaskScheduler is used to manage and schedule tasks using a thread pool.
 */
public class TaskScheduler {

    private final ScheduledExecutorService executorService;
    private final Map<String, ScheduledFuture<?>> scheduledTasks;

    /**
     * The constructor for the TaskScheduler class.
     * @param poolSize The number of threads in the pool.
     */
    public TaskScheduler(int poolSize) {
        this.executorService = Executors.newScheduledThreadPool(poolSize);
        this.scheduledTasks = new ConcurrentHashMap<>();
    }

    /**
     * Schedule a task to be executed periodically.
     * @param taskId The ID of the task.
     * @param task The task to be executed.
     * @param initialDelay The delay before the task is first executed.
     * @param period The period between successive executions.
     * @param unit The time unit of the initialDelay and period parameters.
     */
    public void scheduleTask(String taskId, Runnable task, long initialDelay, long period, TimeUnit unit) {
        if (scheduledTasks.containsKey(taskId)) {
            throw new IllegalArgumentException("Task with ID " + taskId + " is already scheduled.");
        }
        ScheduledFuture<?> scheduledTask = executorService.scheduleAtFixedRate(task, initialDelay, period, unit);
        scheduledTasks.put(taskId, scheduledTask);
    }

    /**
     * Cancel a scheduled task.
     * @param taskId The ID of the task.
     * @return True if the task was cancelled, false otherwise.
     */
    public boolean cancelTask(String taskId) {
        ScheduledFuture<?> scheduledTask = scheduledTasks.remove(taskId);
        if (scheduledTask != null) {
            return scheduledTask.cancel(false);
        }
        return false;
    }

    /**
     * Reschedule a task to be executed periodically.
     * @param taskId The ID of the task.
     * @param task The task to be executed.
     * @param initialDelay The delay before the task is first executed.
     * @param period The period between successive executions.
     * @param unit The time unit of the initialDelay and period parameters.
     */
    public void rescheduleTask(String taskId, Runnable task, long initialDelay, long period, TimeUnit unit) {
        cancelTask(taskId);
        scheduleTask(taskId, task, initialDelay, period, unit);
    }

    /**
     * Shutdown the task scheduler, stopping all tasks and shutting down the thread pool.
     */
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
                if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {
                    System.err.println("Executor did not terminate");
                }
            }
        } catch (InterruptedException ie) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    /**
     * The main method for the TaskScheduler class.
     * @param args The command line arguments.
     */
    public static void main(String[] args) {
        TaskScheduler scheduler = new TaskScheduler(2);
        Runnable task = () -> System.out.println("Task executed at " + new Date());

        scheduler.scheduleTask("task1", task, 0, 5, TimeUnit.SECONDS);

        try {
            Thread.sleep(15000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        scheduler.cancelTask("task1");
        scheduler.shutdown();
    }
}
```

## Options
- `-v, --version`: Show the current version of the tool and exit.
- `o, --output`: Specify the output folder for the processed files. If not provided, the default folder is **fusion_output** in the current directory.
- `h, --help`: Show the help message with usage details and exit.

## Features
- Automatically generates structured comments and documentation for source code.
- Supports multiple programming languages (identified via file extension).
- Handles multiple files at once (no batch processing yet).
- Allows custom output directories to store the processed files.

## License
This project is licensed under the MIT License - see the `LICENSE` file for details.