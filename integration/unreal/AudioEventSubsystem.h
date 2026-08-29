#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "AudioEventSubsystem.generated.h"

USTRUCT(BlueprintType)
struct FAudioEventOptions
{
    GENERATED_BODY()
    UPROPERTY(BlueprintReadWrite, Category="Audio") FVector Position = FVector::ZeroVector;
    UPROPERTY(BlueprintReadWrite, Category="Audio") bool bHasPosition = false;
    UPROPERTY(BlueprintReadWrite, Category="Audio") float Intensity = -1.f;
};

UCLASS()
class UAudioEventSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;
    UFUNCTION(BlueprintCallable, Category="Audio Kit", meta=(WorldContext="WorldContextObject"))
    static void PostAudioEvent(UObject* WorldContextObject, FName EventId, FAudioEventOptions Options);
    UFUNCTION(BlueprintCallable, Category="Audio Kit") void SetRtpc(FName Name, float Value);
    UFUNCTION(BlueprintCallable, Category="Audio Kit") void SetSnapshot(FName Name, float FadeMs = 50.f);
    void SetListener(const FVector& Position, const FVector& Forward);
private:
    void Dispatch(FName EventId, const FAudioEventOptions& Options);
};
