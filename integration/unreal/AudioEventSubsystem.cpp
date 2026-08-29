#include "AudioEventSubsystem.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"

void UAudioEventSubsystem::Initialize(FSubsystemCollectionBase& Collection) { Super::Initialize(Collection); }
void UAudioEventSubsystem::Deinitialize() { Super::Deinitialize(); }

void UAudioEventSubsystem::PostAudioEvent(UObject* WorldContextObject, FName EventId, FAudioEventOptions Options)
{
    if (!WorldContextObject) return;
    UWorld* World = WorldContextObject->GetWorld();
    if (!World) return;
    if (UGameInstance* GI = World->GetGameInstance())
        if (UAudioEventSubsystem* Sys = GI->GetSubsystem<UAudioEventSubsystem>())
            Sys->Dispatch(EventId, Options);
}

void UAudioEventSubsystem::SetRtpc(FName Name, float Value) {}
void UAudioEventSubsystem::SetSnapshot(FName Name, float FadeMs) {}
void UAudioEventSubsystem::SetListener(const FVector& Position, const FVector& Forward) {}
void UAudioEventSubsystem::Dispatch(FName EventId, const FAudioEventOptions& Options)
{
    // Map EventId to MetaSound / Wwise. Never load a raw filename from gameplay.
}
