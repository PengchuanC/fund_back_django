from django.urls import path


from api import views

urlpatterns = [

    path(r"search/fundlist", views.SearchViews.as_view()),

    path(r"plot/branch", views.BranchView.as_view()),
    path(r"plot/exist", views.ExistViews.as_view()),
    path(r"plot/scale", views.ScaleViews.as_view()),
    path(r"plot/comp", views.CompanyViews.as_view()),
    path(r"plot/scale&year", views.ScaleYearViews.as_view()),
    path(r"plot/manager", views.PlotManagerViews.as_view()),
    path(r'plot/', views.PlotViews.as_view()),

    path(r"summary", views.SummaryViews.as_view()),
    path(r"summary/info", views.SummaryInfoViews.as_view()),
    path(r"summary/bc", views.BranchClassifyViews.as_view()),

    path(r"filter/filter", views.FilterViews.as_view()),
    path(r"filter/advance_filter", views.AdvanceViews.as_view()),
    path(r"filter/info", views.FilterBasicInfoViews.as_view()),
    path(r"filter/info/result", views.InfoResultViews.as_view()),

    path(r"fundinfo", views.PerformanceViews.as_view()),
    path(r"fundinfo/style", views.StyleViews.as_view()),
    path(r"fundinfo/style&benchmark", views.StyleAndBenchmarkViews.as_view()),
    path(r"fundinfo/plotperformance", views.PlotPerformanceViews.as_view()),

    path(r"manager", views.ManagerViews.as_view()),
    path(r"manager/managed", views.ManagedViews.as_view()),

    path(r"attr/stock", views.BrinsonViews.as_view()),
    path(r"attr/bond", views.BondAttributionViews.as_view()),
    path(r"attr/rpt_date", views.RptDateViews.as_view()),
    path(r"attr/branch", views.FundBranchViews.as_view()),

    path(r"asset", views.AssetViews.as_view()),

    path(r"portfolio", views.PortfolioViews.as_view()),
    path(r"portfolio/date", views.PortfolioDateViews.as_view()),
    path(r"portfolio/info", views.PortfolioInfoViews.as_view()),

    path(r'nav', views.NavOfPrivateFundViews.as_view()),

    path(r'benchmark', views.BenchmarkNameViews.as_view()),

    path(r"compare/type", views.ProductTypeViews.as_view()),
    path(r"compare/filter", views.ProductFilterViews.as_view())
]
