import { ResponsiveLine } from "@nivo/line";
import { useTheme } from "@mui/material";
import { tokens } from "../theme";
import { mockLineData as data } from "../data/mockData"; //
import axios from "axios";
import React, { useState, useEffect } from "react";
import {Button, Box} from '@mui/material';
import Papa from "papaparse";


const LineChart = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  
  const [chartData, setChartData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  useEffect(() => {
    Papa.parse("/predictions_with_dates.csv", {
      header: true,
      download: true,
      complete: (results) => {
        // Transform the data into nivo's required format
        const actualData = results.data
          .filter(item => item.Date && item.Actual_Price)
          .map(item => ({
            x: item.Date,
            y: parseFloat(item.Actual_Price)
          }));
        
        const predictedData = results.data
          .filter(item => item.Date && item.Predicted_Price)
          .map(item => ({
            x: item.Date,
            y: parseFloat(item.Predicted_Price)
          }));
  
        setChartData([
          {
            id: "Actual Price",
            data: actualData
          },
          {
            id: "Predicted Price",
            data: predictedData
          }
        ]);
      },
      error: (error) => {
        console.error("Error while parsing CSV:", error);
      },
    });
  }, []);

  const handleClick = async () => {
    try {
      setIsLoading(true);
      
      const response = await fetch('http://localhost:8000/getRealTime', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ realtime: true, try: "received" }),
        credentials: 'include',
        mode: 'cors'
      });
  
      if (!response.ok) {
        throw new Error('Failed to fetch real-time prediction');
      }
  
      const result = await response.json();
      
      // Handle successful response
      console.log('Real-time prediction:', result);
      
    } catch (error) {
      console.error('Error fetching real-time prediction:', error);
    } finally {
      setIsLoading(false);
    }
  };
  

  return (
    <Box sx={{ position: 'relative', height: '100%' }}>
      <Button
        component="label"
        role={undefined}
        variant="contained"
        tabIndex={-1}
        sx={{
          position: 'absolute',
          right: 20,
          zIndex: 1,
          backgroundColor: colors.blueAccent[500],
          color: colors.grey[100], 
          fontWeight: "bold",
          fontSize: "12px",
          padding: "5px 10px",
          '&:hover': {
            backgroundColor: colors.blueAccent[700]
          }
        }}
        onClick={handleClick}
        disabled={isLoading} // Optional: disable during loading
      >
        {isLoading ? 'Loading...' : 'Get Real Time Prediction'}
      </Button>

      <ResponsiveLine
        data={chartData}
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
        colors={{ scheme: 'nivo' }}
        margin={{ top: 40, right: 125, bottom: 40, left: 60 }}
        xScale={{
          type: "time",
          format: "%Y-%m-%d",
          precision: "day"
        }}
        xFormat="time:%b, %Y" // Format for tooltips
        yScale={{
          type: "linear",
          min: "auto",
          max: "auto",
          stacked: false,
          reverse: false,
        }}
        yFormat=" >-.2f"
        curve="catmullRom"
        axisTop={null}
        axisRight={null}
        axisBottom={{
          format: "%b, %Y",
          tickValues: "every 1 month", // Show only monthly ticks
          orient: "bottom",
          tickSize: 3,
          tickPadding: 3,
          tickRotation: -30, // Rotate for better readability
          legend: "",
          legendOffset: 40,
          legendPosition: "middle",
        }}
        axisLeft={{
          orient: "left",
          tickValues: 5,
          tickSize: 3,
          tickPadding: 5,
          tickRotation: 0,
          legend: "Price",
          legendOffset: -40,
          legendPosition: "middle",
        }}
        enableGridX={false}
        enableGridY={false}
        pointSize={0.4} 
        pointColor={{ from: 'serieColor' }}
        pointBorderWidth={1}
        pointBorderColor={{ from: 'serieColor' }}
        useMesh={true}
        enableSlices="x"
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
    </Box>
  );
};

export default LineChart;
