import multiprocessing
from typing import List


class ProcessBaseData:
    def __init__(self,
                 Id: int = None):
        self.Id: int = Id


class TaskData:
    def __init__(self,
                 Data: ProcessBaseData = None,
                 SubProcessId: int = None,
                 IsFinished: bool = False,
                 IsProcessed: bool = False):
        self.Data: ProcessBaseData = Data
        self.SubProcessId: int = SubProcessId
        self.IsFinished: bool = IsFinished
        self.IsProcessed: bool = IsProcessed


class ProcessData:
    def __init__(self,
                 Process: any = None,
                 SubProcessId: int = None,
                 IsFinished: bool = False):
        self.Process: multiprocessing.Process = Process
        self.SubProcessId: int = SubProcessId
        self.IsFinished: bool = IsFinished


class ParallelMultiProcessing:
    def __init__(self, number_of_process=5):
        self.number_of_process = number_of_process

    def configure_process(self):
        self.manager = multiprocessing.Manager()
        # Define a list (queue) for tasks and computation results
        self.tasks = self.manager.Queue()
        self.results = self.manager.Queue()
        self.task_list: List[TaskData] = []
        # Create process pool with four processes
        num_cores = multiprocessing.cpu_count()
        self.pool = multiprocessing.Pool(processes=self.number_of_process)
        self.processes: List[ProcessData] = []

    def start_processes(self, process_id, job_id, process_function):
        # Initiate the worker processes
        for i in range(self.number_of_process):
            # Set process name
            sub_process_id = i
            process_name = 'P%i' % sub_process_id
            # Create the process, and connect it to the worker function
            new_process = multiprocessing.Process(target=process_function,
                                                  args=(
                                                      process_id, job_id, sub_process_id, process_name, self.tasks,
                                                      self.results))
            # Add new process to the list of processes
            process_data = ProcessData(Process=new_process, SubProcessId=sub_process_id)
            self.processes.append(process_data)
            # Start the process
            new_process.start()

    def add_task(self, task):
        self.tasks.put(task)
        self.task_list.append(task)

    def finish_tasks(self):
        # Quit the worker processes by sending them -1
        for i in range(self.number_of_process):
            finish_task = TaskData(IsFinished=True)
            self.tasks.put(finish_task)

    def check_unfinished_processes(self):

        for process_data in self.processes:
            if process_data.IsFinished == False and not process_data.Process.is_alive():
                print(f"Unfinished process found. SubProcessId:{process_data.SubProcessId}")
                process_data.IsFinished = True
                # data = TaskData(SubProcessId=process_data.SubProcessId, IsFinished=True)
                # self.results.put(data)

    def check_all_processes_finish(self):
        check_finish = True
        unfinished_process_list = []
        for process_data in self.processes:
            if process_data.IsFinished == False:
                check_finish = False
                unfinished_process_list.append(str(process_data.SubProcessId))
                # data = TaskData(SubProcessId=process_data.SubProcessId, IsFinished=True)
                # self.results.put(data)
        process_join = ",".join(unfinished_process_list)
        print(f"All processes are expected to end . SubProcessId:{process_join}")
        return check_finish

    def check_processes(self, result_function):
        # Read calculation results
        while True:
            # Read result
            new_result: TaskData = self.results.get()
            # Have a look at the results
            if new_result.IsFinished:
                # Process has finished
                for process_data in self.processes:
                    if process_data.SubProcessId == new_result.SubProcessId:
                        process_data.IsFinished = True
                self.check_unfinished_processes()
                if self.check_all_processes_finish():
                    break
            else:
                for task in self.task_list:
                    if task.Data.Id == new_result.Data.Id:
                        print(f"Task is finished :{task.Data}")
                        task.IsProcessed = True
                result_function(new_result)

    def unprocessed_tasks(self) -> List[TaskData]:
        unprocessed_task_list = [task for task in self.task_list if task.IsProcessed == False]
        return unprocessed_task_list
