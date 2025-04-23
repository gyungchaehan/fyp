import { Box, useTheme, Button } from "@mui/material";
import Header from "../../components/Header";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Typography from "@mui/material/Typography";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { tokens } from "../../theme";
import { useNavigate } from "react-router-dom";

const FAQ = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const navigate = useNavigate();
  const handleButtonClick = () => {
    navigate("/form"); // Replace with your desired form route
  };

  return (
    <Box m="20px">
      <Header title="FAQ" subtitle="Frequently Asked Questions Page" />

      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography color={colors.greenAccent[500]} variant="h5">
            How is the model constructed?
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
          Our project involves three main stages: 
          <br></br>
          <Typography fontWeight="600">1. Time Series Analysis</Typography>
          We used Long Short-Term Memory (LSTM) techniques to model and forecast crude oil prices based on historical trends. Moreover, we will develop an NLP pipeline using the pre-trained model sentiment analysis to gauge sentiment related to crude oil price movements.
          <br></br>
          <Typography fontWeight="600">2. Integration & Prediction</Typography>
          We integrated outputs from both historical oil prices and NLP to create a comprehensive feature set for predictions. Using a BiGRU model, we generated precise predictions of future crude oil prices.
          <br></br>
          <Typography fontWeight="600">3. Web Application Stage</Typography>
          We developed a web application for users to view real-time predictions and assess their accuracy against historical data, hence why you're on this site right now :)
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography color={colors.greenAccent[500]} variant="h5">
            Which Large Language Model (LLM) is being used?
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            We used a pre-trained Large Language Model (DeepSeek-R1-Distill-Llama-8B) to automatically summarize market-related news articles and then leverages VADER sentiment analysis related to crude oil price movements.
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography color={colors.greenAccent[500]} variant="h5">
            What dataset is being used?
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            We utilized Yahoo Finance API to acquire historical oil prices and The News API for the news articles from 1 January 2021 up to 10 October 2024.
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography color={colors.greenAccent[500]} variant="h5">
            What is the accuracy? How is the outcome? 
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            We achieved an accuracy of 95% on our test set, with a Mean Absolute Error (MAE) of 0.7783 and a Mean Squared Error (MSE) of 1.0491. The model's predictions closely align with actual prices, demonstrating its reliability and effectiveness in forecasting crude oil prices.
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography color={colors.greenAccent[500]} variant="h5">
            How does it compare to other projects?
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            Our project stands out due to its unique combination of time series analysis and sentiment analysis, providing a more comprehensive approach to crude oil price prediction. While many projects focus solely on historical data or sentiment analysis, our model integrates both aspects, resulting in improved accuracy and reliability.
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Box display="flex" justifyContent="end" mt="20px">
        <Button type="button" onClick={handleButtonClick} color="secondary" variant="contained" sx={{mb:1.5}}>
          Submit a Question
        </Button>
      </Box>
    </Box>
  );
};

export default FAQ;

