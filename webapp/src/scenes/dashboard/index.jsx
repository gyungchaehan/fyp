import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../theme";
import { mockTransactions } from "../../data/mockData";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import Header from "../../components/Header";
import LineChart from "../../components/LineChart";
import BarChart from "../../components/BarChart";
import TimeBox from "../../components/TimeBox";
import VideoBox from "../../components/VideoBox";
import NewsBox from "../../components/NewsBox";
import UserInput from "../../components/UserInput";
import AccessTimeFilledOutlinedIcon from '@mui/icons-material/AccessTimeFilledOutlined';
import { useState } from "react";

const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const [period, setPeriod] = useState("d");
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  const handlePredictionSuccess = (successMessage) => {
    setMessage(successMessage);
    setIsError(false);
  };

  const handlePredictionError = (errorMessage) => {
    setMessage(errorMessage);
    setIsError(true);
  };

  return (
    <Box m="20px">
      {/* HEADER */}
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Header title="Oil Price Prediction" subtitle="Welcome to your dashboard" />

        <Box>
          <Button
            sx={{
              backgroundColor: colors.blueAccent[700],
              color: colors.grey[100],
              fontSize: "14px",
              fontWeight: "bold",
              padding: "10px 20px",
            }}
          >
            <DownloadOutlinedIcon sx={{ mr: "10px" }} />
            Download Reports
          </Button>
        </Box>
      </Box>

      {/* GRID & CHARTS */}
      <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="140px"
        gap="20px"
      >
        {/* ROW 1 */}
        <Box
          gridColumn="span 6"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="space-evenly"
        >
          <TimeBox
            title= "US-Eastern Time"
            timeZone= "America/New_York"
            icon={
              <AccessTimeFilledOutlinedIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box>
        <Box
          gridColumn="span 6"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="space-evenly"
        >
          <TimeBox
            title= "Hong Kong"
            timeZone= "Asia/Hong_Kong"
            icon={
              <AccessTimeFilledOutlinedIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box>

        {/* ROW 2 */}
        <Box
          gridColumn="span 8"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
        >
          <Box
            mt="25px"
            p="0 30px"
            display="flex "
            justifyContent="space-between"
            alignItems="center"
          >
            <Box>
              <Typography
                variant="h5"
                fontWeight="600"
                color={colors.grey[100]}
              >
                Our Test Set Prediction vs. Actual Prices
              </Typography>
            </Box>
          </Box>
          <Box height="250px" m="-20px 0 0 0">
            <LineChart isDashboard={true} /> 
          </Box>
        </Box>
        <Box
          gridColumn="span 4"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
          p="30px"
        >
          <Typography variant="h5" fontWeight="600">
            Current News
          </Typography>
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            mt="25px"
          >
            <VideoBox />
          </Box>
        </Box>

        {/* ROW 3 */}
        <Box
          gridColumn="span 4"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
          p="30px"
        >
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            borderBottom={`4px solid ${colors.primary[500]}`}
            colors={colors.grey[100]}
            p="15px"
          >
            <Typography color={colors.grey[100]} variant="h5" fontWeight="600">
              News Articles
            </Typography>
          </Box>
          <Box
            sx={{
              maxHeight: '80%', // Set a fixed height for the scrollable area
              overflowY: 'auto', // Enable vertical scrolling
            }}
          >
            <NewsBox />
          </Box>
        </Box>
        {/* <Box
          gridColumn="span 4"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
          p="30px"
        >
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            borderBottom={`4px solid ${colors.primary[500]}`}
            colors={colors.grey[100]}
            p="15px"
          >
            <Typography color={colors.grey[100]} variant="h5" fontWeight="600">
              Get Prediction
            </Typography>
          </Box>
          <Box
            sx={{
              maxHeight: '80%',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center', // Horizontally centers child elements
              justifyContent: 'center', // Vertically centers (if needed)
              textAlign: 'center', // Centers text content
              gap: 2, // Adds spacing between elements
              mt: '10px',
              width: '100%' // Ensures full width for proper centering
            }}
          >
            <Typography color={colors.grey[100]} variant="p">
              Insert a CSV file containing the sentiment_score and historical_price to get the next-day prediction. 
            </Typography>
            <Typography color={colors.greenAccent[500]} variant="p" fontWeight={600} sx={{ mt: -0.5}}>
              Please ensure that there are at least 14 data points within it.
            </Typography>
            <UserInput onSuccess={handlePredictionSuccess} onError={handlePredictionError}/>
            {message && (<Typography 
              color={isError ? colors.redAccent[500] : colors.greenAccent[500]}
              variant="body1"
              sx={{ mt: -0.5}}
              fontWeight={600}>
              {message}
            </Typography>)}
          </Box>
        </Box> */}
        <Box
          gridColumn="span 8"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
        >
          <Typography
            variant="h5"
            fontWeight="600"
            sx={{ padding: "30px 30px 0 30px" }}
          >
            Evaluation of Forecasting Performace for Oil Prices
          </Typography>
          <Box height="250px" mt="-20px">
            <BarChart isDashboard={true} />
          </Box>
        </Box>

      </Box>
    </Box>
  );
};

export default Dashboard;
