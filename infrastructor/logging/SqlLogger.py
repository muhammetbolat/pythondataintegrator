from datetime import datetime
from multiprocessing.context import Process
from injector import inject

from infrastructor.IocManager import IocManager
from infrastructor.data.DatabaseSessionManager import DatabaseSessionManager
from infrastructor.data.Repository import Repository
from infrastructor.dependency.scopes import IScoped
from infrastructor.logging.ConsoleLogger import ConsoleLogger
from models.configs.ApiConfig import ApiConfig
from models.configs.DatabaseConfig import DatabaseConfig
from models.dao.common.Log import Log


class SqlLogger(IScoped):
    @inject
    def __init__(self,
                 api_config: ApiConfig,
                 console_logger: ConsoleLogger,
                 database_session_manager: DatabaseSessionManager,
                 ):
        self.console_logger = console_logger
        self.api_config = api_config
        self.database_session_manager = database_session_manager
        self.data_integration_repository: Repository[Log] = Repository[
            Log](database_session_manager)

    @staticmethod
    def log_to_db(type_of_log, log_string, job_id=None):
        api_config: ApiConfig = IocManager.injector.get(ApiConfig)
        console_logger: ConsoleLogger = IocManager.injector.get(ConsoleLogger)
        database_config = IocManager.injector.get(DatabaseConfig)
        database_session_manager = DatabaseSessionManager(database_config=database_config,api_config=api_config)
        log_repository: Repository[Log] = Repository[
            Log](database_session_manager)
        log_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        comment = f'Data Integrator {api_config.environment}'
        try:
            log = Log(TypeId=type_of_log, Content=log_string[0:4000], LogDatetime=log_datetime,
                                           JobId=job_id, Comments=comment)
            log_repository.insert(log)
            database_session_manager.commit()
        except Exception as ex:
            console_logger.error(f'Sql logging getting error{ex}')
        finally:
            console_logger.info(f'{type_of_log} - {log_string}')
            database_session_manager.close()

    #######################################################################################
    def logger_method(self, type_of_log, log_string, job_id=None):
        SqlLogger.log_to_db(type_of_log, log_string, job_id)
        # Process(target=SqlLogger.log_to_db(type_of_log, log_string, job_id), name="Log Process", args=(type_of_log, log_string, job_id,)).start()

    #######################################################################################
    def error(self, error_string, job_id=None):
        self.logger_method(4, error_string, job_id)

    #######################################################################################
    def info(self, info_string, job_id=None):
        self.logger_method(2, info_string, job_id)
