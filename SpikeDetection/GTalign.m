raw_data=transpose(data)

fs = 24000;

f_data = bandpass(raw_data, [300 3000], fs);



%maximum alignment time stamp
spiketGT=[];

parfor i=1:length(spike_times{1, 1})
    s=f_data(spike_times{1, 1}(i):spike_times{1, 1}(i)+62)
    t=spike_times{1, 1}(i)
    [maxv,maxind]=max(s)
    spiketGT=[spiketGT;t+maxind]
    %plot(f_data(t-10:t+40))
    %hold on 
end

%Aligned spikes dataset

GTaligned=[]

parfor j=1: length(spiketGT(:,1))
    
    s=f_data(spiketGT(j)-15:spiketGT(j)+16)
    GTaligned=[GTaligned,s]
end

GTaligned=transpose(GTaligned)

save(GTaligned)