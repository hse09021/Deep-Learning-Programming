import torch
from torch import nn 
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor

#공개 데이터셋에서 학습데이터를 내려받기
training_data = datasets.FashionMNIST(
        root = "data",
        train = True,
        download = True,
        transform = ToTensor()
)


#공개 데이터셋에서 테스트데이터를 내려받기
test_data = datasets.FashionMNIST(
        root = "data",
        train = False,
        download = True,
        transform = ToTensor()
)

batch_size = 64

#데이터로더를 생성

train_dataloader = DataLoader(training_data, batch_size = batch_size)
test_dataloader = DataLoader(test_data, batch_size = batch_size)

for X,y in test_dataloader:
    print(f"Shape of X [N,C,H,W]:{X.shape}")
    print(f"Shape of y:{y.shape} {y.dtype}")
    break

#학습에 사용할 CPU나 GPU 장치를 얻음
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using {device} device")

#모델을 정의함

class NeuralNetwork(nn.Module):
    def __init__(self):
        super(NeuralNetwork,self).__init__()
        self.flattern = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28*28,512),
            nn.ReLU(),
            nn.Linear(512,512),
            nn.ReLU(),
            nn.Linear(512,10),
        )
        
    def forward(self,x):
        x = self.flattern(x)
        logits = self.linear_relu_stack(x)
        return logits
    
model = NeuralNetwork().to(device)
print(model)
    
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.SGD(model.parameters(),lr=1e-3)

def train(dataloader, model, loss_fn, optimizer):
    size = len(dataloader.dataset)
    for batch, (X,y) in enumerate(dataloader):
        X,y = X.to(device), y.to(device) # GPU 나 CPU 사용을 위한 tensor 생성
        
        #예측 오류 계산
        pred = model(X)
        loss = loss_fn(pred,y)
        
        #역전파
        optimizer.zero_grad() # 매개변수의 grad 속성을 초기화
        loss.backward() # 오류역전파 알고리즘 수행, gradient 계산    
        optimizer.step() #신경망 parameter 업데이트
        
        if batch % 100 == 0:
            loss, current = loss.item(), batch*len(X)
            print(f"loss:{loss: > 7f} [{current:>5d}/{size: >5d}]")
 
def test(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval() #테스트 단계에서 drop이나 batch normaolization 수행하지 않도록 함
    test_loss, correct = 0,0
    with torch.no_grad():
         for X,y in dataloader:
             X,y = X.to(device), y.to(device)
             pred = model(X)
             test_loss += loss_fn(pred,y).item()
             correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    test_loss /= num_batches
    correct /= size
    print(f"Test Error:\n Accurach:{(100*correct): > 0.1f}%, Avg loss:{test_loss:>8f} \n")
    
    
epochs = 10
for t in range(epochs):
    print(f"Epoch {t+1}\n _______________________")
    train(train_dataloader, model, loss_fn, optimizer)
    test(test_dataloader,model,loss_fn)
print("Done!")

torch.save(model.state_dict(), "model.pth")
print("Saved Pytorch Model State to model.pth")
            
            

        

