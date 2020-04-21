from readurl import *
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def fun_exp(x, a, b):
    return a * np.exp(b * x)


def fun_logt(x, L, x0, k):
    """
    x: argument
    L: saturation
    x0: time when half saturation is reached"""
    #k = k_CN
    y = L / (1 + np.exp(-k * (x - x0)))
    return y


def dN_N(countries, start_date, x0 = 5):
    """
    dN as function of N (linear for exponential growth)
    countries: list of dictionaries
    x0: int increase during last days
    """
    for i in range(len(countries)):
        time = countries[i]['time']
        total = countries[i]['total']

        start_ind = np.argwhere(time == start_date)[0][0]   # start analysis on this state (index)
        time, total = time[start_ind:], total[start_ind:]   # crop data
        incr = total[x0:] - total[:-x0]
        plt.loglog(total[x0:], incr,'--',label=countries[i]['countrylabel'])

    plt.loglog(total[x0:], total[x0:],'--', lw=1, color='grey', label='total Cases')
    plt.title('Today %s, Increase (last %s days) vs. Total' % (time[-1], x0),fontsize=15)
    plt.xlabel('Total cases',fontsize=15)
    plt.ylabel('New incr. in last %s days'%x0,fontsize=15)
    plt.tick_params(labelsize=15,length=5)
    plt.grid()
    plt.legend(fontsize=13)
    plt.show()


def fit_total(country, start_date, n_fit, func):
    time, total = country['time'], country['total']
    start_ind = np.argwhere(time == start_date)[0][0]  # start analysis on this state (index)
    time, total = time[start_ind:], total[start_ind:]  # crop data

    fit_data = country['total'][-n_fit:]
    fit_daycount = np.arange(len(total))[-n_fit:]
    if func == 'exp':
        popt, _ = curve_fit(fun_exp, fit_daycount, fit_data, p0=(20000, 0.2))

        xx = np.linspace(len(total) - 15, len(total) + 4)
        plt.semilogy(np.arange(len(total)), total, 'o', label=country['countrylabel'])
        plt.semilogy(xx, fun_exp(xx, *popt), '--', lw=2, label=r'exp. fit: $\sim e^{%.2f\, t}$' % popt[1])

        plt.title('%s, today %d, next day: +%.0f' % (
        country['countrylabel'], total[-1], -total[-1] + fun_exp(len(total) + 1, *popt)), fontsize=14)
        plt.xlabel('Day (+ %s)' % start_date, fontsize=13)
        plt.ylabel('# of cases.', fontsize=13)
        plt.tick_params(labelsize=13, length=5)
        plt.legend(fontsize=12, loc='upper left')
        plt.grid()
        plt.show()

    elif func == 'log':
        popt, _ = curve_fit(fun_logt, np.arange(len(time)), total, p0=(60000, 30, 0.25))
        xx = np.linspace(0, len(total) + 1)
        plt.plot(np.arange(len(total)), total, 'o', label=country['countrylabel'])
        plt.plot(xx, fun_logt(xx, *popt), '--', lw=2, label='logt_fit: k=%.2f' % popt[2])

        L, x0, k = popt[0], popt[1], popt[2]
        halftime = time[int(x0) + 1]  # date on which half saturation is reached
        plt.axvline(x0, ls='--', color='black', label=r'on %s half reached' % halftime)
        plt.title('%s, saturation %.0f' % (country['countrylabel'], L), fontsize=14)
        plt.xlabel('Day (+ %s)' % start_date, fontsize=13)
        plt.ylabel('# of cases.', fontsize=13)
        plt.tick_params(labelsize=13, length=5)
        plt.legend(fontsize=12, loc='upper left')
        plt.grid()
        plt.show()
    else:
        print('func=%s not specified' % func)



def daily_incr(country, start_date=None):
    """
    plot daily increase over total
    country: dic with time and total
    start_sate: str that has form of entry in country['time']
    """
    time, total = country['time'], country['total']
    if start_date is None:
        start_ind = 0
    else:
        start_ind = np.argwhere(time == start_date)[0][0]  # start analysis on this state (index)
    time, total = time[start_ind:], total[start_ind:]      # crop data

    dayincr = total[1:] - total[:-1]
    X_add = np.arange(1, len(total))

    plt.plot(X_add,dayincr,'o--')
    plt.title('%s, daily increase' % country['countrylabel'],fontsize=14)
    plt.xlabel('Day %s' % time[0],fontsize=13)
    plt.ylabel('# per day.',fontsize=13)
    plt.tick_params(labelsize=13,length=5)
    plt.grid()
    plt.show()


def growth_rate(country, start_date, n_fit):
    """
    make exponential fit over each bunch of n_fit days. Plot evolution of growth rate and doubling time
    country: dic with time and total
    n_fit: int days over which exponential fit is performed
    """
    time, total = country['time'], country['total']
    start_ind = np.argwhere(time == start_date)[0][0]  # start analysis on this state (index)
    time, total = time[start_ind:], total[start_ind:]  # crop data

    goback = len(total) - n_fit          # go back to first week
    k_hist = np.zeros(goback + 1)
    for day_i in np.arange(goback + 1):
        takeind = day_i + np.arange(n_fit) # make fit over these indices
        fit_data = total[takeind]
        fit_daycount = takeind
        popt, _ = curve_fit(fun_exp, fit_daycount, fit_data, p0=(20000,0.2))
        k_hist[day_i] = popt[1]              # take exponential grwoth rate from fit
    doubleT_hist = np.log(2)/k_hist       # doubling time

    fig, ax1 = plt.subplots()

    ax1.plot(np.arange(len(k_hist)), k_hist,'bs--',ms=5,lw=2)
    ax1.set_ylabel('Growth rate',fontsize=15,color='b')  # we already handled the x-label with ax1
    ax1.tick_params(axis='y', labelcolor='b')

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.plot(np.arange(len(k_hist)), doubleT_hist,'ro--',lw=2)
    ax2.set_xlabel('Date (+ March 14th)',fontsize=15)
    ax2.set_ylabel('Doubling time (Day)',fontsize=15,color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    fig.tight_layout()
    plt.show()

def main():
    germany = get_data('germany')
    italy = get_data('italy')
    france = get_data('france')
    china = get_data('china')
    us = get_data('us')

    start_date = "Mar01"  # analysis starting on
    country = germany
    x0 = 5  # increase during last x0 days
    n_fit = 7  # make fit over one week (last week)

    countries = [china, germany, italy, us]
    dN_N(countries, start_date, x0)               # increase over total
    fit_total(country, start_date, n_fit, 'exp')
    fit_total(country, start_date, n_fit, 'log')
    daily_incr(country, start_date)
    growth_rate(country, start_date, n_fit)




if __name__ == '__main__':
    main()