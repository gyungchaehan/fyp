import React, { useState, useEffect } from "react";
import { Box, Typography, useTheme } from "@mui/material";
import { tokens } from "../theme";
import { format, toZonedTime } from "date-fns-tz";

const TimeBox = ({ title, icon, timeZone }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  // State to store the current date and time
  const [currentDateTime, setCurrentDateTime] = useState({
    date: "",
    time: "",
  });

  // Function to get the current date and time for the given time zone
  const getCurrentDateTime = (timeZone) => {
    const date = new Date();
    const utcDate = toZonedTime(date, timeZone);
    return {
      date: format(utcDate, "yyyy-MM-dd", { timeZone }),
      time: format(utcDate, "HH:mm:ss", { timeZone }),
    };
  };

  // Update the date and time every second
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentDateTime(getCurrentDateTime(timeZone));
    }, 1000); // Update every 1000ms (1 second)

    return () => clearInterval(interval); // Cleanup interval on component unmount
  }, [timeZone]); // Re-run effect if `timeZone` changes

  const { date, time } = currentDateTime;

  return (
    <Box width="100%" m="0 30px">
      <Box display="flex" justifyContent="space-evenly">
        <Box display="flex" justifyContent="space-between" sx={{ marginTop: 1 }}>
          {icon}
          <Typography
            variant="h4"
            fontWeight="bold"
            sx={{ color: colors.grey[100], marginLeft: 2 }}
          >
            {title}
          </Typography>
        </Box>
        <Box justifyItems="center">
          <Typography
            variant="h4"
            fontWeight="bold"
            sx={{ color: colors.grey[100] }}
          >
            {date}
          </Typography>
          <Typography
            variant="h5"
            fontStyle="italic"
            sx={{ color: colors.greenAccent[600] }}
          >
            {time}
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default TimeBox;
