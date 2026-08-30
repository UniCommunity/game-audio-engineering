// FMOD Studio adaptive mixer — Unreal subsystem.
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "FmodAudioSubsystem.generated.h"

UCLASS()
class UFmodAudioSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()

public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;
	virtual void Deinitialize() override;

	UFUNCTION(BlueprintCallable, Category = "FMOD")
	void InitializeFmod();

	UFUNCTION(BlueprintCallable, Category = "FMOD")
	void PostAudioEvent(FName EventId, const FVector& Location);

	UFUNCTION(BlueprintCallable, Category = "FMOD")
	void SetIntensity(float Value);

	UFUNCTION(BlueprintCallable, Category = "FMOD")
	void SetCrowdVolume(float Value);

	UFUNCTION(BlueprintCallable, Category = "FMOD")
	void SetPlayerHealth(float Normalized);

	UFUNCTION(BlueprintCallable, Category = "FMOD")
	void SetCommentaryActive(bool bActive);

	UFUNCTION(BlueprintCallable, Category = "FMOD")
	void SetSnapshot(FName SnapshotName);

	UFUNCTION(BlueprintCallable, Category = "FMOD")
	void IngestCrowdMic(float Rms);

private:
	void SetGlobal(const TCHAR* Name, float Value);
	bool bReady = false;
};
