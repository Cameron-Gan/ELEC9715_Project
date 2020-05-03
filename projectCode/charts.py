from projectCode.aCAT import Predispatch, Dispatch
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
from projectCode.helperFunctions import convert_to_datetime

sns.set_style("darkgrid")

#Color palatte
blue, red = sns.color_palette("muted", 2)

def chart_prices(state):
    forecast = Predispatch()
    forecast = forecast.get_table("REGION_PRICE")
    forecast_prices = forecast[forecast['REGIONID'] == state]
    x_f = forecast_prices['PERIODID'].astype(int)
    x_f = x_f.apply(convert_to_datetime)
    # print(type(x_f))
    y_f = forecast_prices['RRP'].astype(float)

    dispatch = Dispatch()
    dispatch = dispatch.get_table("REGION_PRICE")
    dispatch_price = dispatch[dispatch["REGIONID"] == state]
    x_d = pd.to_datetime(dispatch_price['SETTLEMENTDATE'], format='\"%Y/%m/%d %H:%M:%S\"')

    # print(x_d)
    y_d = dispatch_price['RRP'].astype(float)

    fig, (past_ax, forecast_ax) = plt.subplots(1, 2, figsize=(17,9))
    plt.subplots_adjust(wspace=0, hspace=0)

    past_ax.set_title('Past Prices')
    past_ax.plot(x_d, y_d, color=blue, lw=3)
    past_ax.fill_between(x_d, 0, y_d, alpha=.3, color=blue)
    locator1 = mdates.AutoDateLocator()
    formatter1 = mdates.ConciseDateFormatter(locator1)
    past_ax.xaxis.set_major_locator(locator1)
    past_ax.xaxis.set_major_formatter(formatter1)

    forecast_ax.set_title('Forecast Prices')
    # forecast_ax = past_ax.twiny()
    forecast_ax.plot(x_f, y_f, color=red, lw=3)
    forecast_ax.fill_between(x_f, 0, y_f, alpha=.3, color=red)
    locator2 = mdates.AutoDateLocator()
    formatter2 = mdates.ConciseDateFormatter(locator2)
    forecast_ax.xaxis.set_major_locator(locator2)
    forecast_ax.xaxis.set_major_formatter(formatter2)

    max_y = max([y_f.max(), y_d.max()])
    min_y = min([y_f.min(), y_d.min()])

    forecast_ax.set_ylim([min_y * 0.9, max_y * 1.1])
    past_ax.set_ylim([min_y * 0.9, max_y * 1.1])
    forecast_ax.get_yaxis().set_ticklabels([])

    forecast_ax.set_xlim(left=x_f.min())
    past_ax.set_xlim(right=x_d.max())

    fig.suptitle('Wholesale Prices')
    fig.tight_layout()
    plt.show()

def chart_demand(state):
    forecast = Predispatch()
    forecast = forecast.get_table("REGION_SOLUTION")
    forecast_prices = forecast[forecast['REGIONID'] == state]
    x_f = forecast_prices['PERIODID'].astype(int)
    x_f = x_f.apply(convert_to_datetime)
    y_f = forecast_prices['CLEAREDSUPPLY'].astype(float)

    dispatch = Dispatch()
    dispatch = dispatch.get_table("REGION_SOLUTION")
    dispatch_price = dispatch[dispatch["REGIONID"] == state]
    x_d = pd.to_datetime(dispatch_price['SETTLEMENTDATE'], format='\"%Y/%m/%d %H:%M:%S\"', exact=False)
    # print(x_d)
    y_d = dispatch_price['CLEAREDSUPPLY'].astype(float)

    fig, (past_ax, forecast_ax) = plt.subplots(1, 2, figsize=(17, 9))
    past_ax.set_title('Past Demand')
    past_ax.plot(x_d, y_d, color=blue, lw=3)
    past_ax.fill_between(x_d, 0, y_d, alpha=.3, color=blue)
    locator1 = mdates.AutoDateLocator()
    formatter1 = mdates.ConciseDateFormatter(locator1)
    past_ax.xaxis.set_major_locator(locator1)
    past_ax.xaxis.set_major_formatter(formatter1)

    forecast_ax.set_title('Forecast Demand')
    # forecast_ax = past_ax.twiny()
    forecast_ax.plot(x_f, y_f, color=red, lw=3)
    forecast_ax.fill_between(x_f, 0, y_f, alpha=.3, color=red)
    locator2 = mdates.AutoDateLocator()
    formatter2 = mdates.ConciseDateFormatter(locator2)
    forecast_ax.xaxis.set_major_locator(locator2)
    forecast_ax.xaxis.set_major_formatter(formatter2)

    max_y = max([y_f.max(), y_d.max()])
    min_y = min([y_f.min(), y_d.min()])

    forecast_ax.set_ylim([min_y * 0.9, max_y * 1.1])
    past_ax.set_ylim([min_y * 0.9, max_y * 1.1])
    forecast_ax.get_yaxis().set_ticklabels([])

    forecast_ax.set_xlim(left=x_f.min())
    past_ax.set_xlim(right=x_d.max())

    fig.suptitle('Total Demand')
    fig.tight_layout()
    plt.show()

def show_load_schedule(model):
    time_steps = model.time_steps
    cheapest_path = model.cheapest_path.path
    df = pd.DataFrame({'onoffpath': cheapest_path,
                       'time': time_steps})
    df.set_index('time', inplace=True)
    fig, ax = plt.subplots(figsize=(17, 9))
    ax.set_ylim([0,1])
    ax.bar(df.index, df['onoffpath'], width=.02, color=red)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    # set major ticks format
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    ax.set_title('On Off and Maintain Schedule of Load')
    fig.tight_layout()
    plt.show()

def show_state_price(model):
    time_steps = model.time_steps
    df = pd.DataFrame({'state': model.cheapest_path.state_value,
                       'time': time_steps})
    price = model.forecast_price.copy()
    price = price.reset_index()
    df = pd.concat([df, price[['RRP', 'PERIODID']]], axis=1)
    df.set_index('PERIODID', inplace=True)
    fig, ax = plt.subplots(figsize=(17, 9))

    ax.plot(df.index, df['state'], color=blue, lw=3)
    ax.fill_between(df.index, 0, df['state'], color=blue, alpha=0.3, label='State')
    ax.set_ylim([0,1])
    ax.set_ylabel('State')
    ax2 = ax.twinx()
    ax2.set_ylabel('Price')
    ax2.plot(df.index, df['RRP'], color=red, lw=3, label='Price')

    ax.set_title('State of Storage and Price')
    fig.legend(loc='upper right')
    fig.tight_layout()
    plt.show()

