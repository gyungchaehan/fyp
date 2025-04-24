import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LineChart from './LineChart';
import 'jest-fetch-mock';

// Mock window.URL for CSV parsing
global.URL.createObjectURL = jest.fn();

jest.mock('d3-interpolate', () => ({
  interpolate: jest.fn(),
}));

jest.mock('papaparse', () => ({
  parse: jest.fn((_, config) => {
    config.complete({
      data: [
        { Date: '2024-09-26', Actual_Price: 100, Predicted_Price: 105 },
        { Date: '2024-09-27', Actual_Price: 102, Predicted_Price: 104 }
      ],
      meta: {},
    });
  }),
}));

beforeEach(() => {
  fetch.resetMocks();
});

test('renders line chart with initial CSV data', async () => {
  render(<LineChart />);

  await waitFor(() => {
    expect(screen.getByText('Actual Price')).toBeInTheDocument();
    expect(screen.getByText('Predicted Price')).toBeInTheDocument();
  });
});

test('fetches and displays real-time data on button click', async () => {
  fetch.mockResponseOnce(JSON.stringify({
    data: {
      actual_prices: [{ date: '2024-09-26', price: 100 }],
      predicted_prices: [{ date: '2024-09-26', price: 105 }],
    },
  }));

  render(<LineChart />);
  
  await userEvent.click(screen.getByRole('button', { name: /get real time prediction/i }));

  await waitFor(() => {
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/getRealTime',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
    );
    expect(screen.getByText('Show Realtime Data')).toBeInTheDocument();
  });
});

test('toggles between historical and real-time data', async () => {
  fetch.mockResponseOnce(JSON.stringify({
    data: {
      actual_prices: [{ date: '2024-09-26', price: 100 }],
      predicted_prices: [{ date: '2024-09-26', price: 105 }],
    },
  }));

  render(<LineChart />);
  
  // Initial state
  expect(screen.queryByText('Show Realtime Data')).not.toBeInTheDocument();

  // Fetch real-time data
  await userEvent.click(screen.getByRole('button', { name: /get real time prediction/i }));
  
  // Wait for switch to appear
  const switchLabel = await screen.findByText('Show Realtime Data');
  const toggle = switchLabel.nextElementSibling.querySelector('input');
  
  // Toggle the switch
  await userEvent.click(toggle);
  expect(toggle).toBeChecked();
});