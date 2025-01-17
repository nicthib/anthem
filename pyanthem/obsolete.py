def synth(self):
		'''
		
		'''
		fs = 44100
		r = .5 # release for note
		#r_mat = np.linspace(1, 0, num=int(fs*r))
		#r_mat = np.vstack((r_mat,r_mat)).T
		currnote = -1
		ext = 11
		note = [[0] * 8 for i in range(3)]
		raws = np.zeros((int(fs*(np.max(self.nd['st'])+ext)),2))
		nnotes = len(self.nd['st'])
		for i in range(len(self.nd['st'])):
			if currnote != self.nd['note'][i]:
				currnote = self.nd['note'][i]
				for mag in range(8): # Load up new notes
					for length in range(3):
						fn = str(currnote+1)+'_'+str(mag)+'_'+str(length+1)+'.ogg';
						note[length][mag],notused = read(os.path.join(self.package_path,'AE',fn))
			L = self.nd['en'][i]-self.nd['st'][i]
			L = min(L,10-r)
			if L > 1:
				raw = note[2][int(np.ceil(self.nd['mag'][i]/16-1))]#[0:int(L*fs)] # Truncate to note length plus release
			elif 1 > L > .25:
				raw = note[1][int(np.ceil(self.nd['mag'][i]/16-1))]#[0:int(L*fs)] # Truncate to note length plus release
			elif L < .25:
				raw = note[0][int(np.ceil(self.nd['mag'][i]/16-1))]#[0:int(L*fs)] # Truncate to note length plus release
			#raw[-int(fs*r):] *= r_mat
			inds = range(int(self.nd['st'][i][0]*fs),int(self.nd['st'][i][0]*fs)+len(raw))
			raws[inds,:] += raw
			if self.display:
				self.status['text'] = f'Status: writing audio file, {i+1} out of {nnotes} notes written'
				self.update()
		raws = raws[:-fs*(ext-1),:] # Crop wav
		raws = np.int16(raws/np.max(np.abs(raws)) * 32767)
		wavwrite(os.path.join(self.cfg['save_path'],self.cfg['file_out'])+'.wav',fs,raws)
		
	def neuralstream(self):
		'''
		
		'''
		C0 = 16.352
		fs = 44100
		freqs = [C0*2**(i/12) for i in range(128)]
		true_fr = (self.cfg['fr']*self.cfg['speed'])/100
		ns = int(fs*len(self.data['H_fp'].T)/true_fr)
		t1 = np.linspace(0,len(self.data['H_fp'].T)/self.cfg['fr'],len(self.data['H_fp'].T))
		t2 = np.linspace(0,len(self.data['H_fp'].T)/self.cfg['fr'],ns)
		H = np.zeros((len(t2),))
		nchan = len(self.data['H_fp'])
		for n in range(nchan):
			Htmp = self.data['H_fp'][n,:]
			Htmp[Htmp<0] = 0
			Htmp = interp1d(t1,Htmp)(t2)
			H += np.sin(2*np.pi*freqs[self.keys[n]]*t2)*Htmp
			Hstr = 'H_fp'
			if self.display:
				self.status['text'] = f'Status: Writing audio: {n+1} out of {nchan} channels...'
				self.update()
		wav = np.hstack((H[:,None],H[:,None]))
		wav = np.int16(wav/np.max(np.abs(wav)) * 32767)
		wavwrite(os.path.join(self.cfg['save_path'],self.cfg['file_out'])+'.wav',fs,wav)
		