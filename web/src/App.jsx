import React from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import InteractiveSimulator from './components/InteractiveSimulator';
import ArchitectureBento from './components/ArchitectureBento';
import GlitchSection from './components/GlitchSection';
import BenchmarksExplorer from './components/BenchmarksExplorer';
import CliSdkDocs from './components/CliSdkDocs';
import IncidentRegister from './components/IncidentRegister';
import Footer from './components/Footer';

export default function App() {
  return (
    <div className="app-container">
      <Navbar />
      <main>
        <Hero />
        <InteractiveSimulator />
        <ArchitectureBento />
        <GlitchSection />
        <BenchmarksExplorer />
        <CliSdkDocs />
        <IncidentRegister />
      </main>
      <Footer />
    </div>
  );
}
