import { ResponsiveLine } from "@nivo/line";
import { useTheme } from "@mui/material";
import { tokens } from "../theme";
import { mockLineData as data } from "../data/mockData";
import axios from "axios";
import React, { useState, useEffect } from "react";
import { Button, Box, FormControlLabel, Switch, Typography } from '@mui/material'; // Ensure these are imported
import Papa from "papaparse";


const LineChart = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  
  const [testData, setTestData] = useState([]);
  const [realtimeData, setRealtimeData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showRealtime, setShowRealtime] = useState(false); 
  
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
  
        setTestData([
          {
            id: "Actual Price",
            data: actualData
          },
          {
            id: "Predicted Price",
            data: predictedData
          }
        ]);
        console.log(testData);
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
      const transformed = [
        {
          id: "Actual Price",
          data: result.data.actual_prices.map(item => ({
            x: item.date,
            y: item.price
          })),
        },
        {
          id: "Predicted Price",
          data: result.data.predicted_prices.map((item, index) => ({
            // Align dates with actual prices where they overlap
            x: index < result.data.actual_prices.length 
              ? result.data.actual_prices[index].date 
              : item.date,
            y: item.price
          })),
        }
      ];      
      setRealtimeData(transformed);
      setShowRealtime(true); 
      console.log(transformed)
      
    } catch (error) {
      console.error('Error fetching real-time prediction:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const getChartData = () => {
    if (showRealtime && realtimeData.length > 0) {
      return realtimeData;
    }
    return testData;
  };

  return (
    <Box sx={{ position: 'relative', height: '100%' }}>
      <Box sx={{ 
        position: 'absolute', 
        right: 20,
        top: 10,
        zIndex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        alignItems: 'flex-end'
      }}>
        <Button
          variant="contained"
          sx={{
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
          disabled={isLoading}
        >
          {isLoading ? 'Loading...' : 'Get Real Time Prediction'}
        </Button>

        {realtimeData.length > 0 && (
            <Box sx={{
              display: 'flex',
              alignItems: 'center',
              backgroundColor: colors.primary[400],
              padding: '4px 8px',
              borderRadius: '4px'
            }}>
              <Typography variant="body2" sx={{mr:0.5, color: colors.grey[100], fontWeight:"bold" }}>
                Show Realtime Data
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={showRealtime}
                    onChange={() => setShowRealtime(!showRealtime)}
                    color="secondary"
                  />
                }
                label=""
                sx={{ mr: -1 }}
              />
            </Box>
        )}
      </Box>

      <ResponsiveLine
        data={getChartData()}
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
          precision: "day",
          min: showRealtime ? "2024-09-26" : "auto",
          max: showRealtime ? "2024-10-02" : "auto",
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
        curve="linear"
        axisTop={null}
        axisRight={null}
        axisBottom={{
          format: showRealtime ? "%b %d" : "%b, %Y",
          tickValues: showRealtime ? "every 1 day" : "every 1 month",
          orient: "bottom",
          tickSize: 3,
          tickPadding: 10,
          tickRotation: showRealtime ? -45 : -30,
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
        pointSize={showRealtime ? 0.8 : 0.4}
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
