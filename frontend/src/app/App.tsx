import { BrowserRouter, useRoutes } from 'react-router-dom';
import { Providers } from './providers';
import { routes } from './router';
import { ErrorBoundary, ToastContainer } from '../shared/components';

function AppRoutes() {
  return useRoutes(routes);
}

function App() {
  return (
    <Providers>
      <BrowserRouter>
        <ErrorBoundary>
          <AppRoutes />
        </ErrorBoundary>
        <ToastContainer />
      </BrowserRouter>
    </Providers>
  );
}

export default App;
