import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import ProductSelectionPage from './pages/ProductSelectionPage'
import HomePage from './pages/HomePage'
import ResultsPage from './pages/ResultsPage'

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LoginPage />} />
                <Route path="/products" element={<ProductSelectionPage />} />
                <Route path="/dashboard/:productId" element={<HomePage />} />
                <Route path="/results/:jobId" element={<ResultsPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App
