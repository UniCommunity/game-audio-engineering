#include "FmodAudioSubsystem.h"

#if WITH_FMOD
#include "FMODStudioModule.h"
#include "FMODBlueprintStatics.h"
#endif

void UFmodAudioSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
}

void UFmodAudioSubsystem::Deinitialize()
{
	Super::Deinitialize();
	bReady = false;
}

void UFmodAudioSubsystem::InitializeFmod()
{
#if WITH_FMOD
	UFMODBlueprintStatics::PlayEvent2D(this, FSoftObjectPath(TEXT("event:/music/state/explore")), true);
	UFMODBlueprintStatics::PlayEvent2D(this, FSoftObjectPath(TEXT("event:/ambience/hall")), true);
	UFMODBlueprintStatics::PlayEvent2D(this, FSoftObjectPath(TEXT("event:/crowd/live")), true);
	SetSnapshot(FName(TEXT("normal")));
	bReady = true;
#endif
}

void UFmodAudioSubsystem::PostAudioEvent(FName EventId, const FVector& Location)
{
	if (!bReady) return;
#if WITH_FMOD
	const FString Path = FString::Printf(TEXT("event:/%s"), *EventId.ToString().Replace(TEXT("."), TEXT("/")));
	UFMODBlueprintStatics::PlayEventAtLocation(this, FSoftObjectPath(Path), FTransform(Location), true);
#endif
}

void UFmodAudioSubsystem::SetGlobal(const TCHAR* Name, float Value)
{
#if WITH_FMOD
	UFMODBlueprintStatics::SetGlobalParameterByName(FName(Name), Value);
#endif
}

void UFmodAudioSubsystem::SetIntensity(float Value)
{
	SetGlobal(TEXT("intensity"), FMath::Clamp(Value, 0.f, 1.f));
}

void UFmodAudioSubsystem::SetCrowdVolume(float Value)
{
	SetGlobal(TEXT("crowd_volume"), FMath::Clamp(Value, 0.f, 1.f));
}

void UFmodAudioSubsystem::SetPlayerHealth(float Normalized)
{
	SetGlobal(TEXT("player_health"), FMath::Clamp(Normalized, 0.f, 1.f));
}

void UFmodAudioSubsystem::SetCommentaryActive(bool bActive)
{
	SetGlobal(TEXT("commentary_active"), bActive ? 1.f : 0.f);
}

void UFmodAudioSubsystem::SetSnapshot(FName SnapshotName)
{
#if WITH_FMOD
	const FString Path = FString::Printf(TEXT("snapshot:/%s"), *SnapshotName.ToString());
	UFMODBlueprintStatics::PlayEvent2D(this, FSoftObjectPath(Path), true);
#endif
}

void UFmodAudioSubsystem::IngestCrowdMic(float Rms)
{
	SetCrowdVolume(Rms);
}
