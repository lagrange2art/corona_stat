from readurl import *
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def fun_exp(x, a, k):
    """exponential function a * np.exp(k * x)
    """
    return a * np.exp(k * x)


def fun_logt(x, L, x0, k):
    """logarithmic function L / (1 + np.exp(-k * (x - x0)))
    x: argument
    L: saturation
    x0: time when half saturation is reached"""
    return  L/(1 + np.exp(-k * (x - x0)))


def dN_N(countries, start_date, n = 5):
    """
    change within n days as function of current population (linear for exponential growth)
    :param countries: list of dictionaries with time and total
    :param n: int increase during last days
    """
    for i in range(len(countries)):
        time = countries[i]['time']
        total = countries[i]['total']

        start_ind = np.argwhere(time == start_date)[0][0]   # start analysis on this state (index)
        time, total = time[start_ind:], total[start_ind:]   # crop data
        incr = total[n:] - total[:-n]
        plt.loglog(total[n:], incr,'--',label=countries[i]['countrylabel'])

    plt.loglog(total[n:], total[n:],'--', lw=1, color='grey', label='total Cases')
    plt.title('Today %s, Increase (last %s days) vs. Total' % (time[-1], n),fontsize=15)
    plt.xlabel('Total cases',fontsize=15)
    plt.ylabel('New incr. in last %s days'%n,fontsize=15)
    plt.tick_params(labelsize=15,length=5)
    plt.grid()
    plt.legend(fontsize=13)
    plt.show()


class Analysis(object):
    def __init__(self, **kwargs):
        """
        plot and analyse data, i.e. make exponential and logarithmic fit. Starting from specific date
        :param country dict with time and total
        :param start_sate: str that has form of entry in country['time']
        :param n_fit: int days over which exponential fit is performed
        """
        self.country = kwargs['country']
        self.start_date = kwargs['start_date']
        self.n_fit = kwargs['n_fit']

        # crop data
        time = self.country['time']
        total = self.country['total']
        self.start_ind = np.argwhere(time == self.start_date)[0][0]             # start analysis on this state (index)
        self.time, self.total = time[self.start_ind:], total[self.start_ind:]   # crop data


    def fit_total(self, func):
        if func == 'exp':
            fit_data = self.total[-self.n_fit:]                                 # fit only over last n_fit days
            fit_daycount = np.arange(len(self.total))[-self.n_fit:]             # count days after start_date
            popt, _ = curve_fit(fun_exp, fit_daycount, fit_data, p0=(20000, 0.2))

            xx = np.linspace(len(self.total) - 15, len(self.total) + 4)
            plt.semilogy(np.arange(len(self.total)), self.total, 'o', label=self.country['countrylabel'])
            plt.semilogy(xx, fun_exp(xx, *popt), '--', lw=2, label=r'exp. fit: $\sim e^{%.2f\, t}$' % popt[1])

            plt.title('%s, today %d, next day: +%.0f' % (self.country['countrylabel'],
                                    self.total[-1], -self.total[-1] + fun_exp(len(self.total) + 1, *popt)), fontsize=14)
            plt.xlabel('Day (+ %s)' % self.start_date, fontsize=13)
            plt.ylabel('# of cases.', fontsize=13)
            plt.tick_params(labelsize=13, length=5)
            plt.legend(fontsize=12, loc='upper left')
            plt.grid()
            plt.show()

        elif func == 'log':
            popt, _ = curve_fit(fun_logt, np.arange(len(self.time)), self.total, p0=(60000, 30, 0.25))
            xx = np.linspace(0, len(self.total) + 1)
            plt.plot(np.arange(len(self.total)), self.total, 'o', label=self.country['countrylabel'])
            plt.plot(xx, fun_logt(xx, *popt), '--', lw=2, label='logt_fit: k=%.2f' % popt[2])

            L, x0, k = popt[0], popt[1], popt[2]
            halftime = self.time[int(x0) + 1]  # date on which half saturation is reached
            plt.axvline(x0, ls='--', color='black', label=r'on %s half reached' % halftime)
            plt.title('%s, saturation %.0f' % (self.country['countrylabel'], L), fontsize=14)
            plt.xlabel('Day (+ %s)' % self.start_date, fontsize=13)
            plt.ylabel('# of cases.', fontsize=13)
            plt.tick_params(labelsize=13, length=5)
            plt.legend(fontsize=12, loc='upper left')
            plt.grid()
            plt.show()
        else:
            print('func=%s not specified' % func)



    def daily_incr(self):
        """
        plot daily increase over total
        """
        dayincr = self.total[1:] - self.total[:-1]
        X_add = np.arange(1, len(self.total))

        plt.plot(X_add,dayincr,'o--')
        plt.title('%s, daily increase' % self.country['countrylabel'],fontsize=14)
        plt.xlabel('Day %s' % self.time[0],fontsize=13)
        plt.ylabel('# per day.',fontsize=13)
        plt.tick_params(labelsize=13,length=5)
        plt.grid()
        plt.show()


    def growth_rate(self):
        """
        make exponential fit over each bunch of n_fit days. Plot evolution of growth rate and doubling time
        """
        goback = len(self.total) - self.n_fit          # go back to n_fit days
        k_hist = np.zeros(goback + 1)                  # growth rate for each bunch
        for day_i in np.arange(goback + 1):
            takeind = day_i + np.arange(self.n_fit)    # make fit over these indices
            fit_data = self.total[takeind]
            fit_daycount = takeind
            popt, _ = curve_fit(fun_exp, fit_daycount, fit_data, p0=(20000,0.2))
            k_hist[day_i] = popt[1]                   # take exponential growth rate from fit
        doubleT_hist = np.log(2)/k_hist               # doubling time

        fig, ax1 = plt.subplots()

        ax1.plot(np.arange(len(k_hist)), k_hist,'bs--',ms=5,lw=2)
        ax1.set_ylabel('Growth rate',fontsize=15,color='b')  # we already handled the x-label with ax1
        ax1.tick_params(axis='y', labelcolor='b')

        ax2 = ax1.twinx()                                    # instantiate a second axes that shares the same x-axis
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

    fitting = Analysis(country=country, start_date=start_date, n_fit=n_fit)
    fitting.fit_total('exp')
    fitting.fit_total('log')
    fitting.daily_incr()
    fitting.growth_rate()




if __name__ == '__main__':
    main()