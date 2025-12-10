import { TopNav } from './components/layout/TopNav';
import { LeftColumn } from './components/layout/LeftColumn';
import { CenterColumn } from './components/layout/CenterColumn';
import { RightColumn } from './components/layout/RightColumn';
import { useAppStore } from './stores/appStore';

function App() {
  const {
    user,
    globalStatus,
    activeView,
    navigationCounts,
    efficiencyStats,
    actionCards,
    selectedCardId,
    activeFilter,
    selectedConversation,
    setActiveView,
    setActiveFilter,
    selectCard,
    handleCardAction,
  } = useAppStore();

  return (
    <div className="h-screen flex flex-col bg-surface-base overflow-hidden">
      <TopNav
        user={user}
        globalStatus={globalStatus}
        onSearch={(query) => console.log('Search:', query)}
      />

      <main className="flex-1 flex min-h-0">
        <LeftColumn
          counts={navigationCounts}
          stats={efficiencyStats}
          activeView={activeView}
          onViewChange={setActiveView}
        />

        <CenterColumn
          cards={actionCards}
          selectedCardId={selectedCardId ?? undefined}
          onSelectCard={selectCard}
          onAction={handleCardAction}
          activeFilter={activeFilter}
          onFilterChange={setActiveFilter}
        />

        <RightColumn
          conversation={selectedConversation}
          onTakeOver={() => console.log('Take over thread')}
          onChangePolicy={() => console.log('Change policy')}
        />
      </main>
    </div>
  );
}

export default App;
