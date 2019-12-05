from api.models import FundPerformance
from sync_data.insert import insert


insert(FundPerformance, "t_ff_performance")
