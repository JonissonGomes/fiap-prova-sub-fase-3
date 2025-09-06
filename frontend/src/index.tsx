import React from 'react';
import ReactDOM from 'react-dom/client';
import { ThemeProvider, createTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import App from './App';
import reportWebVitals from './reportWebVitals';

const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
      light: '#9bb5ff',
      dark: '#4c63d2',
    },
    secondary: {
      main: '#764ba2',
      light: '#a478d4',
      dark: '#5a3a7a',
    },
    background: {
      default: '#f5f7fa',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
        contained: {
          boxShadow: '0 4px 14px 0 rgba(0, 0, 0, 0.1)',
          '&:hover': {
            boxShadow: '0 6px 20px 0 rgba(0, 0, 0, 0.15)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 12px 0 rgba(0, 0, 0, 0.08)',
          '&:hover': {
            boxShadow: '0 4px 20px 0 rgba(0, 0, 0, 0.12)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
        elevation1: {
          boxShadow: '0 2px 12px 0 rgba(0, 0, 0, 0.08)',
        },
        elevation2: {
          boxShadow: '0 4px 20px 0 rgba(0, 0, 0, 0.12)',
        },
        elevation3: {
          boxShadow: '0 8px 32px 0 rgba(0, 0, 0, 0.16)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          boxShadow: '0 4px 20px 0 rgba(0, 0, 0, 0.12)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          background: 'linear-gradient(180deg, #f8f9ff 0%, #ffffff 100%)',
          borderRight: '1px solid rgba(102, 126, 234, 0.1)',
        },
      },
    },
    MuiListItem: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '4px 8px',
          '&.Mui-selected': {
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%)',
            },
          },
          '&:hover': {
            background: 'rgba(102, 126, 234, 0.05)',
          },
        },
      },
    },
  },
});

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

// Adicionar estilos globais para garantir scroll
const globalStyles = `
  html, body {
    height: 100%;
    overflow: auto !important;
  }
  
  #root {
    height: 100%;
    overflow: auto;
  }
  
  /* Garantir que modais/dialogs tenham scroll quando necessário */
  .MuiDialog-paper {
    max-height: 90vh;
    overflow-y: auto;
  }
  
  /* Garantir que formulários longos tenham scroll */
  .MuiPaper-root {
    max-height: none;
  }
`;

// Injetar estilos no head
const styleSheet = document.createElement('style');
styleSheet.type = 'text/css';
styleSheet.innerText = globalStyles;
document.head.appendChild(styleSheet);

root.render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
);

reportWebVitals(); 