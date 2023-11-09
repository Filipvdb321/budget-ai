import { Category, MonthTotal, Transaction } from "@/app/api/budget.server";
import { MonthlyForcast } from "@/app/api/es-forcasting.server";
import { percentageToStatusClass } from "@/app/utils/styling";
import {
  formatAmount,
  formatYnabAmount,
  totalPercentageSpent,
} from "@/app/utils/ynab";
import { format } from "path";
import { MonthlySpendingChart } from "../charts/mothly-spending-chart";
import { transactionsToMonthlySpendingData } from "../charts/util";

type Props = {
  monthTotal: MonthTotal;
  monthPercentage: number;
  forecast: MonthlyForcast;
  transactions: Array<Transaction>;
};
const MonthTotalOverview = ({
  monthTotal,
  monthPercentage,
  forecast,
  transactions,
}: Props) => {
  const percentage = totalPercentageSpent(monthTotal);

  const statusClass = percentageToStatusClass(percentage);
  return (
    <div className="card bg-base-100 shadow-xl mb-5">
      <div className="card-body p-0.5 sm:p-5">
        <div className="flex flex-wrap w-full">
          <div className="w-full sm:w-1/2 md:w-1/2 lg:w-1/4">
            <table className="table w-80">
              <thead>
                <tr>
                  <th>Total activity</th>
                  <th>Total available</th>
                  <th>Total budgeted</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>{formatYnabAmount(monthTotal.totalActivity, true)}</td>
                  <td>{formatYnabAmount(monthTotal.totalBalance)}</td>
                  <td>{formatYnabAmount(monthTotal.totalBudgeted)}</td>
                </tr>
                <tr>
                  <td>Month Progress</td>
                  <td colSpan={2}>
                    <progress
                      className={`progress progress-${percentageToStatusClass(
                        monthPercentage
                      )}`}
                      value={monthPercentage}
                      max="100"
                    ></progress>
                  </td>
                </tr>
                <tr>
                  <td>Budget Progress</td>
                  <td colSpan={2}>
                    <progress
                      className={`progress progress-${percentageToStatusClass(
                        percentage
                      )}`}
                      value={percentage}
                      max="100"
                    ></progress>
                  </td>
                </tr>
                <tr>
                  <td>Forecasted Remaining amount</td>
                  <td colSpan={2}>
                    {formatAmount(forecast.predictedRemainingAmount)}
                  </td>
                </tr>
                <tr>
                  <td>Forecasted Daily amount</td>
                  <td colSpan={2}>
                    {formatAmount(forecast.predictedRemainingPerDay)}
                  </td>
                </tr>
                <tr>
                  <td>Actual Remaing per day amount</td>
                  <td colSpan={2}>
                    {formatAmount(forecast.actualRemainingPerDay)}
                  </td>
                </tr>
                <tr>
                  <td>Extra suggested</td>
                  <td colSpan={2}>
                    {formatAmount(forecast.extraAmountNeeded)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div className="w-full sm:w-1/2 md:w-1/2 lg:w-3/4">
            <MonthlySpendingChart
              spendingData={transactionsToMonthlySpendingData(transactions)}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default MonthTotalOverview;
