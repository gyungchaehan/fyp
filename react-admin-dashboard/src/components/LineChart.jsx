import { ResponsiveLine } from "@nivo/line";
import { useTheme } from "@mui/material";
import { tokens } from "../theme";
import { mockLineData as data } from "../data/mockData"; //
import axios from "axios";
import React, { useState, useEffect } from "react";

// import yahooFinance from 'yahoo-finance2';

const getDateRange = (period) => {
  // FIX RANGES - need to discuss
  if (period === "y") {
    return { from: "2022-01-01", to: "2022-12-31" };
  } else if (period === "m") {
    return { from: "2022-01-01", to: "2022-01-31" };
  } else if (period === "d") {
    return { from: "2022-01-01", to: "2022-01-07" };
  } else {
    // DEAFULT IS YEAR 
    return { from: "2022-01-01", to: "2022-12-31" };
  }
};


const LineChart = ({ isCustomLineColors = false, isDashboard = false, period="y", symbol = "MAREL.IC"}) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  
  //change code and feed to linechart , add period as a parameter to linechart  -DONT KNOW ID THIS PART WORKS
  const [chartData, setChartData] = useState([]);

  // Fetch the historical data when the component mounts or when the period prop changes.
  // useEffect(() => {
  //   async function fetchData() {
  //     const { from, to } = getDateRange(period);
  //     try {
  //       const history = await yahooFinance.historical({
  //         symbol: "CT=F",
  //         from: from,
  //         to: to,
  //         period: "d"
  //       });
  //       // Convert fetched history to the format expected by ResponsiveLine.
  //       // Here we assume each record in history includes a 'date' and 'close' property.
  //       const lineData = [
  //         {
  //           id: "CT=F",
  //           data: history.map((item) => ({
  //             x: new Date(item.date).toLocaleDateString(),
  //             y: item.close
  //           }))
  //         }
  //       ];
  //       setChartData(lineData);
  //     } catch (error) {
  //       console.error("Error fetching historical data:", error);
  //     }
  //   }
  //   fetchData();
  // }, [period]);

  return (
    <ResponsiveLine
      data={data}
      theme={{
        axis: {
          domain: {
            line: {
              stroke: colors.grey[100],
            },
          },
          legend: {
            text: {
              fill: colors.grey[100],
            },
          },
          ticks: {
            line: {
              stroke: colors.grey[100],
              strokeWidth: 1,
            },
            text: {
              fill: colors.grey[100],
            },
          },
        },
        legends: {
          text: {
            fill: colors.grey[100],
          },
        },
        tooltip: {
          container: {
            color: colors.primary[500],
          },
        },
      }}
      colors={isDashboard ? { datum: "color" } : { scheme: "nivo" }} // added
      margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
      xScale={{ type: "point" }}
      yScale={{
        type: "linear",
        min: "auto",
        max: "auto",
        stacked: true,
        reverse: false,
      }}
      yFormat=" >-.2f"
      curve="catmullRom"
      axisTop={null}
      axisRight={null}
      axisBottom={{
        orient: "bottom",
        tickSize: 0,
        tickPadding: 5,
        tickRotation: 0,
        legend: isDashboard ? undefined : "transportation", // added
        legendOffset: 36,
        legendPosition: "middle",
      }}
      axisLeft={{
        orient: "left",
        tickValues: 5, // added
        tickSize: 3,
        tickPadding: 5,
        tickRotation: 0,
        legend: isDashboard ? undefined : "count", // added
        legendOffset: -40,
        legendPosition: "middle",
      }}
      enableGridX={false}
      enableGridY={false}
      pointSize={8}
      pointColor={{ theme: "background" }}
      pointBorderWidth={2}
      pointBorderColor={{ from: "serieColor" }}
      pointLabelYOffset={-12}
      useMesh={true}
      legends={[
        {
          anchor: "bottom-right",
          direction: "column",
          justify: false,
          translateX: 100,
          translateY: 0,
          itemsSpacing: 0,
          itemDirection: "left-to-right",
          itemWidth: 80,
          itemHeight: 20,
          itemOpacity: 0.75,
          symbolSize: 12,
          symbolShape: "circle",
          symbolBorderColor: "rgba(0, 0, 0, .5)",
          effects: [
            {
              on: "hover",
              style: {
                itemBackground: "rgba(0, 0, 0, .03)",
                itemOpacity: 1,
              },
            },
          ],
        },
      ]}
    />
  );
};

export default LineChart;
