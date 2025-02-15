"use client";
import React, { useEffect, useState } from "react";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale
} from "chart.js";
import { Line } from "react-chartjs-2";
import { Category, MonthlyForcast } from "common-ts";
import { getPrediction } from "../../api/math.client";
import 'chartjs-adapter-date-fns';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale
);

type Props = {
    forecast: MonthlyForcast;
    categories: Category[];
    budgetId: string;
};

type SimulationData = {
    [date: string]: {
        balance: number;
        balance_diff?: number;
        changes: Array<{
            amount: number;
            category: string;
            reason: string;
            is_simulation?: boolean;
            memo?: string;
        }>;
    };
};

type PredictionData = {
    [simulationName: string]: SimulationData;
};

export const PredictionChart = ({ forecast, categories, budgetId }: Props) => {
    const [predictionData, setPredictionData] = useState<PredictionData | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Functie om een kleur te genereren op basis van index
    const getSimulationColor = (index: number) => {
        const colors = [
            "rgb(75, 192, 192)",  // cyaan voor actual balance
            "rgb(255, 99, 132)",  // rood
            "rgb(54, 162, 235)",  // blauw
            "rgb(255, 206, 86)",  // geel
            "rgb(153, 102, 255)", // paars
            "rgb(255, 159, 64)"   // oranje
        ];
        return colors[index % colors.length];
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: "top" as const,
            },
            title: {
                display: true,
                text: "Balance Prediction",
                font: {
                    size: 16
                }
            },
            tooltip: {
                callbacks: {
                    title: function (tooltipItems: any) {
                        const date = new Date(tooltipItems[0].raw.x);
                        return `Date: ${date.toLocaleDateString('nl-NL', {
                            day: '2-digit',
                            month: 'long',
                            year: 'numeric'
                        })}`;
                    },
                    label: function (context: any) {
                        if (!predictionData) return [];

                        const data = context.raw;
                        const lines = [];

                        // Add balance
                        lines.push(`Balance: €${data.y.toFixed(2)}`);

                        // Add balance difference if available
                        const simulationName = context.dataset.label.endsWith('.json')
                            ? context.dataset.label
                            : context.dataset.label === "Actual Balance" ? "Actual Balance" : context.dataset.label + ".json";

                        const simulation = predictionData[simulationName];
                        if (!simulation) return lines;

                        const dateStr = data.x.toISOString().split('T')[0];
                        const dayData = simulation[dateStr];
                        if (!dayData) return lines;

                        if (dayData.balance_diff) {
                            lines.push(`Balance Difference: €${dayData.balance_diff.toFixed(2)}`);
                        }

                        // Add changes
                        if (dayData.changes && dayData.changes.length > 0) {
                            lines.push('Changes:');
                            dayData.changes.forEach((change: any) => {
                                if (change.amount === 0) return;

                                const sign = change.amount >= 0 ? '+' : '';
                                let line = `${sign}€${change.amount.toFixed(2)} (${change.category}`;
                                if (change.reason) line += ` - ${change.reason}`;
                                line += ')';
                                if (change.is_simulation) line += ' [Simulation]';
                                lines.push(line);
                            });
                        }

                        return lines;
                    }
                }
            }
        },
        scales: {
            x: {
                type: 'time' as const,
                time: {
                    unit: 'day' as const,
                    displayFormats: {
                        day: 'd MMM'
                    }
                },
                ticks: {
                    maxRotation: 0,
                    minRotation: 0,
                    autoSkip: true,
                    maxTicksLimit: 6,
                    align: 'start',
                    font: {
                        size: 11
                    }
                }
            },
            y: {
                type: 'linear' as const,
                display: true,
                position: 'left' as const,
                beginAtZero: true,
                ticks: {
                    callback: function (tickValue: string | number): string {
                        return `€${Number(tickValue).toFixed(0)}`;
                    },
                    maxTicksLimit: 8
                },
                grid: {
                    color: 'rgba(200, 200, 200, 0.2)'
                }
            }
        }
    } as const;

    useEffect(() => {
        const fetchPredictionData = async () => {
            try {
                const data = await getPrediction(budgetId);
                setPredictionData(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'An error occurred while fetching prediction data');
                console.error('Error fetching prediction data:', err);
            }
        };

        fetchPredictionData();
    }, [budgetId]);

    if (error) {
        return <div className="alert alert-error">{error}</div>;
    }

    if (!predictionData) {
        return <div className="loading loading-spinner loading-lg"></div>;
    }

    // Collect all unique dates from all simulations
    const allDates = new Set<string>();
    Object.values(predictionData).forEach(simulation => {
        Object.keys(simulation).forEach(date => allDates.add(date));
    });
    const sortedDates = Array.from(allDates).sort();

    const datasets = Object.entries(predictionData).map(([simulationName, simulationData], index) => {
        // Verwijder .json uit de naam en maak het leesbaar
        const displayName = simulationName === "Actual Balance"
            ? "Actual Balance"
            : simulationName.replace(".json", "").split("_").map(word =>
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(" ");

        // Gebruik index om kleur te bepalen (Actual Balance altijd eerste kleur)
        const color = getSimulationColor(simulationName === "Actual Balance" ? 0 : index + 1);

        // Filter alleen de datums met een balans verandering
        const dataPoints = sortedDates
            .filter(date => {
                const data = simulationData[date];
                return data && data.balance_diff !== 0;
            })
            .map(date => ({
                x: new Date(date),
                y: simulationData[date].balance
            }));

        return {
            label: displayName,
            data: dataPoints,
            borderColor: color,
            backgroundColor: 'transparent',
            borderWidth: 2,
            tension: 0.1,
            pointRadius: 2,
            pointHoverRadius: 4,
            datalabels: {
                display: false  // Verberg de datalabels
            }
        };
    });

    const chartData = {
        datasets
    };

    return (
        <div style={{ height: '400px' }}>
            <Line options={options} data={chartData} />
        </div>
    );
};

export default PredictionChart; 