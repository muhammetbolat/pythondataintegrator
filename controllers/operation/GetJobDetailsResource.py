from injector import inject
from controllers.common.models.CommonModels import CommonModels
from controllers.operation.models.DataOperationModels import DataOperationModels
from infrastructor.api.ResourceBase import ResourceBase
from infrastructor.data.DatabaseSessionManager import DatabaseSessionManager
from infrastructor.data.Repository import Repository
from models.dao.integration.PythonDataIntegration import PythonDataIntegration
from models.dao.integration.PythonDataIntegrationLog import PythonDataIntegrationLog


@DataOperationModels.ns.route('/GetJobDetails/<string:code>')
class GetJobDetailsResource(ResourceBase):
    @inject
    def __init__(self,
                 database_session_manager: DatabaseSessionManager,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.database_session_manager = database_session_manager
        self.python_data_integration_log_repository: Repository[PythonDataIntegrationLog] = Repository[
            PythonDataIntegrationLog](
            database_session_manager)

        self.python_data_integration_repository: Repository[PythonDataIntegration] = Repository[PythonDataIntegration](
            database_session_manager)

    @DataOperationModels.ns.marshal_with(CommonModels.SuccessModel)
    def get(self, code):
        """
        Job details with code
        """
        python_data_integration = self.python_data_integration_repository.first(Code=code)

        if python_data_integration is None:
            return "Code Not Found"
        result = DataOperationModels.get_data_operation_job_models(python_data_integration.Jobs)
        return CommonModels.get_response(result)