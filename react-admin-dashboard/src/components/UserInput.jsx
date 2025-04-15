import React, { useRef } from 'react';
import Button from '@mui/material/Button';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { styled } from '@mui/material/styles';
import { useTheme } from "@mui/material";
import { tokens } from "../theme";

const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

const UserInput = ({ onSuccess, onError }) => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    try {
      // Client-side validation
      if (!file.name.endsWith('.csv')) {
        throw "Please upload a CSV file"; // Simple string error
      }

      const MAX_SIZE = 2 * 1024 * 1024;
      if (file.size > MAX_SIZE) {
        throw "File size exceeds 2MB limit"; // Simple string error
      }

      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        body: formData,
        credentials: 'include',
        mode: 'cors'
      });

      const result = await response.json();
      
      if (!response.ok) {
        // Extract the simple message from API error
        throw result.detail?.msg || "Invalid file format";
      }

      onSuccess(`Predicted value: ${result.prediction.toFixed(2)}`);
      
    } catch (error) {
      // Now 'error' is always a string
      onError(typeof error === 'string' ? error : "Upload failed");
    } finally {
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <Button
      component="label"
      role={undefined}
      variant="contained"
      tabIndex={-1}
      sx={{
        backgroundColor: colors.blueAccent[500],
        color: colors.grey[100], 
        fontWeight: "bold",
        fontSize: "11px",
        padding: "5px 10px",
        mt: -0.5,
        '&:hover': {
            backgroundColor: colors.blueAccent[700]
        }
      }}
      startIcon={<CloudUploadIcon />}
    >
      Upload files
      <VisuallyHiddenInput 
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        accept=".csv"
      />
    </Button>
  );
};

export default UserInput;